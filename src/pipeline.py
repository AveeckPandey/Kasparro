"""Batch processing pipeline with bounded concurrency, error handling, and reporting."""

import csv
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import settings
from src.models import (
    ParsedResume,
    EligibilityResult,
    CandidateResult,
    BatchSummary,
    ScreeningReport,
    FilterPreferences,
    ScoreBreakdown,
    GitHubMetrics,
)
from src.parsers.resume_parser import ResumeParser
from src.filters.eligibility import EligibilityFilter
from src.enrichment.github_client import GitHubClient
from src.scoring.scorer import CandidateScorer
from src.llm.adapter import get_llm_adapter

logger = logging.getLogger(__name__)


class ScreeningPipeline:
    """Orchestrates candidate resume ingestion, filtering, enrichment, and ranking."""

    def __init__(self, github_token: Optional[str] = None):
        self.github_client = GitHubClient(token=github_token)
        self.llm_adapter = get_llm_adapter()

    def process_directory(
        self,
        input_dir: str | Path,
        preferences: Optional[FilterPreferences] = None,
        max_workers: int = 5,
    ) -> ScreeningReport:
        """Process all resumes in a directory concurrently with bounded worker threads."""
        dir_path = Path(input_dir)
        if not dir_path.exists():
            raise FileNotFoundError(f"Input directory does not exist: {dir_path}")

        # Collect supported files
        supported_exts = {".pdf", ".docx", ".doc", ".txt", ".md"}
        resume_files = [
            f for f in dir_path.iterdir()
            if f.is_file() and f.suffix.lower() in supported_exts
        ]
        resume_files.sort(key=lambda p: p.name)

        if not resume_files:
            logger.warning(f"No resume files found in {dir_path}")
            return ScreeningReport(
                batch_summary=BatchSummary(),
                ranked_candidates=[],
                rejected_candidates=[],
            )

        # Process resumes with bounded concurrency
        eligible_candidates: List[CandidateResult] = []
        rejected_candidates: List[CandidateResult] = []
        failed_count = 0
        parsed_count = 0
        github_cohorts_count = {
            "Veteran Builder": 0,
            "Active Builder": 0,
            "Emerging Developer": 0,
            "Dormant / Minimal": 0,
            "Unlinked / Missing": 0,
        }

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_resume, file_path, preferences): file_path
                for file_path in resume_files
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    cand_result, is_failed = future.result()
                    if is_failed:
                        failed_count += 1
                        rejected_candidates.append(cand_result)
                    else:
                        parsed_count += 1
                        if cand_result.eligible:
                            eligible_candidates.append(cand_result)
                        else:
                            rejected_candidates.append(cand_result)

                        # Tally cohort
                        if cand_result.github_metrics:
                            cohort = cand_result.github_metrics.cohort
                            github_cohorts_count[cohort] = github_cohorts_count.get(cohort, 0) + 1
                        else:
                            github_cohorts_count["Unlinked / Missing"] += 1

                except Exception as exc:
                    logger.error(f"Unexpected error processing {file_path.name}: {exc}")
                    failed_count += 1
                    rejected_candidates.append(
                        CandidateResult(
                            candidate_name=file_path.stem.replace("_", " ").title(),
                            file_name=file_path.name,
                            eligible=False,
                            rejection_reasons=[f"Internal processing error: {str(exc)[:60]}"],
                            reason_50_to_100_words=(
                                f"Candidate {file_path.name} could not be processed due to an unhandled system "
                                f"exception during document ingestion. The file may be corrupt or encoded in an "
                                f"incompatible format. Please verify the resume document integrity."
                            ),
                        )
                    )

        # Sort eligible candidates by total_score descending
        eligible_candidates.sort(key=lambda c: c.total_score, reverse=True)

        # Assign ranks 1 to N
        for idx, candidate in enumerate(eligible_candidates, start=1):
            candidate.rank = idx

        # Sort rejected candidates alphabetically by name
        rejected_candidates.sort(key=lambda c: c.candidate_name)

        # Compute average eligible score
        avg_score = (
            round(sum(c.total_score for c in eligible_candidates) / len(eligible_candidates), 1)
            if eligible_candidates
            else 0.0
        )

        batch_summary = BatchSummary(
            total_resumes=len(resume_files),
            successfully_parsed=parsed_count,
            eligible=len(eligible_candidates),
            rejected=len(rejected_candidates),
            failed_unreadable=failed_count,
            github_cohorts=github_cohorts_count,
            average_score_eligible=avg_score,
        )

        return ScreeningReport(
            batch_summary=batch_summary,
            ranked_candidates=eligible_candidates,
            rejected_candidates=rejected_candidates,
        )

    def _process_single_resume(
        self, file_path: Path, preferences: Optional[FilterPreferences] = None
    ) -> Tuple[CandidateResult, bool]:
        """Process an individual candidate resume through parsing, filtering, scoring, and justification."""
        # 1. Parse File
        resume = ResumeParser.parse_file(file_path)
        if resume.parsing_status != "success":
            failed_result = CandidateResult(
                candidate_name=resume.candidate_name,
                file_name=resume.file_name,
                eligible=False,
                rejection_reasons=[f"Unreadable file: {resume.parsing_status}"],
                matched_skills=[],
                reason_50_to_100_words=(
                    f"The resume file {resume.file_name} could not be parsed successfully ({resume.parsing_status}). "
                    f"Our document ingestion pipeline requires readable text formatting. Please inspect "
                    f"the uploaded file for corruption, password protections, or non-standard font encodings."
                ),
            )
            return failed_result, True

        # 2. Hard Eligibility Check
        eligibility = EligibilityFilter.evaluate(resume, preferences)

        if not eligibility.eligible:
            # Candidate rejected by hard filter
            # Generate narrative reason
            narrative = self.llm_adapter.generate_narrative_reason(
                candidate_name=resume.candidate_name,
                eligible=False,
                total_score=0.0,
                breakdown_dict={},
                strengths=[],
                concerns=[],
                rejection_reasons=eligibility.rejection_reasons,
                matched_skills=eligibility.matched_skills,
                github_summary="Skipped for ineligible candidate",
            )

            rejected_result = CandidateResult(
                rank=None,
                candidate_name=resume.candidate_name,
                file_name=resume.file_name,
                eligible=False,
                total_score=0.0,
                score_breakdown=ScoreBreakdown(),
                matched_skills=eligibility.matched_skills,
                project_summary="Profile did not meet minimum Python and AI/agentic requirements.",
                github_summary="Not enriched (disqualified before scoring).",
                strengths=[],
                concerns=["Failed hard eligibility criteria"],
                rejection_reasons=eligibility.rejection_reasons,
                reason_50_to_100_words=narrative,
                cgpa=resume.cgpa,
                has_related_experience=resume.has_related_experience,
            )
            return rejected_result, False

        # 3. Eligible Candidate: Enrich with GitHub Activity
        gh_metrics, gh_score, gh_summary = self.github_client.enrich_profile(resume.github_username)

        # 4. Score Candidate (100-pt rubric)
        total_score, breakdown, strengths, concerns, penalties, project_summary = (
            CandidateScorer.score_candidate(resume, gh_metrics, gh_score)
        )

        # 5. Generate 50-100 Word Narrative Justification
        narrative = self.llm_adapter.generate_narrative_reason(
            candidate_name=resume.candidate_name,
            eligible=True,
            total_score=total_score,
            breakdown_dict=breakdown.model_dump(),
            strengths=strengths,
            concerns=concerns,
            rejection_reasons=[],
            matched_skills=eligibility.matched_skills,
            github_summary=gh_summary,
        )

        result = CandidateResult(
            rank=None,  # Assigned after batch sorting
            candidate_name=resume.candidate_name,
            file_name=resume.file_name,
            eligible=True,
            total_score=total_score,
            score_breakdown=breakdown,
            matched_skills=eligibility.matched_skills,
            project_summary=project_summary,
            github_summary=gh_summary,
            strengths=strengths,
            concerns=concerns,
            rejection_reasons=[],
            reason_50_to_100_words=narrative,
            github_metrics=gh_metrics,
            cgpa=resume.cgpa,
            has_related_experience=resume.has_related_experience,
            penalties_applied=penalties,
        )

        return result, False

    @staticmethod
    def export_json(report: ScreeningReport, output_path: str | Path) -> None:
        """Export screening report to structured JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_csv(report: ScreeningReport, output_path: str | Path) -> None:
        """Export screening results to tabular CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        all_candidates = report.ranked_candidates + report.rejected_candidates
        fieldnames = [
            "rank", "candidate_name", "eligible", "total_score",
            "ai_project_depth", "python_backend", "cloud_fullstack", "github", "engineering_depth",
            "cgpa", "has_related_experience", "github_cohort", "github_years",
            "github_repos", "github_original_repos", "github_contributions",
            "github_commits", "github_prs", "github_stars",
            "matched_skills", "rejection_reasons", "reason_narrative"
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in all_candidates:
                writer.writerow({
                    "rank": c.rank if c.rank is not None else "Rejected",
                    "candidate_name": c.candidate_name,
                    "eligible": c.eligible,
                    "total_score": c.total_score,
                    "ai_project_depth": c.score_breakdown.ai_project_depth,
                    "python_backend": c.score_breakdown.python_backend,
                    "cloud_fullstack": c.score_breakdown.cloud_fullstack,
                    "github": c.score_breakdown.github,
                    "engineering_depth": c.score_breakdown.engineering_depth,
                    "cgpa": c.cgpa if c.cgpa is not None else "N/A",
                    "has_related_experience": c.has_related_experience,
                    "github_cohort": c.github_metrics.cohort if c.github_metrics else "N/A",
                    "github_years": c.github_metrics.account_age_years if c.github_metrics else 0.0,
                    "github_repos": c.github_metrics.public_repos if c.github_metrics else 0,
                    "github_original_repos": c.github_metrics.original_repos_count if c.github_metrics else 0,
                    "github_contributions": c.github_metrics.total_contributions if c.github_metrics else 0,
                    "github_commits": c.github_metrics.recent_commits if c.github_metrics else 0,
                    "github_prs": c.github_metrics.prs_count if c.github_metrics else 0,
                    "github_stars": c.github_metrics.total_stars if c.github_metrics else 0,
                    "matched_skills": "; ".join(c.matched_skills),
                    "rejection_reasons": "; ".join(c.rejection_reasons),
                    "reason_narrative": c.reason_50_to_100_words,
                })
