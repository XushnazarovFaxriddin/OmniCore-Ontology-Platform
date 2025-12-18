"""
OmniCore Platform v10 - Strategic Meta-AI
Phase 5: Full Autonomy with Human Oversight

v10 spec: evaluate_strategic_goals_quarterly()
- Autonomous planning with human approval for critical changes
- Rollback capability
- Ethical constraints
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from src.common.config import get_settings
from src.common.logging_config import get_logger
from src.common.models import (
    StrategicGoals, StrategicPlan, QuarterlyReview,
    EthicalAlert, generate_operation_id
)

logger = get_logger("ai.strategic")


@dataclass
class SystemMetrics:
    """Current system metrics for strategic evaluation"""
    ontologies_integrated: int = 0
    mmo_prediction_r2: float = 0.0
    task_success_rate: float = 0.0
    human_interventions_last_quarter: int = 0
    unresolved_ethical_alerts: int = 0
    total_roots: int = 0
    total_causality_links: int = 0
    avg_import_time_ms: float = 0.0
    slm_availability: float = 1.0
    storage_usage_percent: float = 0.0


class HumanOversightInterface:
    """
    v10 Human Oversight Interface

    Handles:
    - Approval requests for critical changes
    - Ethical alerts
    - SIGUSR1 halt signal handling
    """

    def __init__(self):
        self.pending_approvals: List[Dict[str, Any]] = []
        self.ethical_alerts: List[EthicalAlert] = []
        self._halt_requested = False

    async def request_approval(self, plan: StrategicPlan) -> bool:
        """
        Request human approval for a strategic plan.

        v10 requires approval for:
        - New root type proposals
        - MMO metric weight shifts > 20%
        - Ontology from high-bias jurisdiction
        """
        approval_id = generate_operation_id()

        approval_request = {
            "id": approval_id,
            "timestamp": datetime.utcnow().isoformat(),
            "plan": plan.model_dump() if hasattr(plan, 'model_dump') else plan.__dict__,
            "status": "pending",
            "requires_critical_review": plan.requires_human_approval
        }

        self.pending_approvals.append(approval_request)

        logger.info(f"Human approval requested: {approval_id}")
        logger.info(f"Actions: {plan.actions}")

        # In production, this would send notification (Slack/email)
        # For now, auto-approve non-critical changes
        if not plan.requires_human_approval:
            return True

        # Critical changes need manual approval
        return False

    async def raise_ethical_alert(
        self,
        alert_type: str,
        description: str,
        affected_entities: List[str],
        severity: float = 0.8
    ) -> EthicalAlert:
        """Raise an ethical alert for human review"""
        alert = EthicalAlert(
            id=generate_operation_id(),
            timestamp=datetime.utcnow(),
            alert_type=alert_type,
            severity=severity,
            description=description,
            affected_entities=affected_entities,
            requires_approval=severity >= 0.8
        )

        self.ethical_alerts.append(alert)
        logger.warning(f"Ethical alert raised: {alert.id} - {alert_type}")

        return alert

    def check_halt_signal(self) -> bool:
        """Check if SIGUSR1 halt signal was received"""
        return self._halt_requested

    def set_halt(self, value: bool):
        """Set halt state (called by signal handler)"""
        self._halt_requested = value
        if value:
            logger.warning("HALT SIGNAL RECEIVED - Pausing autonomous operations")

    def get_pending_approvals(self) -> List[Dict]:
        """Get list of pending approval requests"""
        return [a for a in self.pending_approvals if a["status"] == "pending"]

    def get_unresolved_alerts(self) -> List[EthicalAlert]:
        """Get unresolved ethical alerts"""
        return [a for a in self.ethical_alerts if not a.resolved]


class StrategicMetaAI:
    """
    v10 Strategic Meta-AI

    Responsible for:
    - Quarterly strategic goal evaluation
    - Autonomous planning with constraints
    - MO evolution recommendations
    - Goal revision proposals
    """

    # Strategic goals from v10 spec
    GOALS = {
        "ontology_coverage": 1000,      # >= 1000 ontologies integrated
        "mmo_accuracy": 0.90,           # >= 0.90 R² score
        "ai_task_success": 0.92,        # >= 0.92 success rate
        "human_intervention": 20,       # <= 20 interventions/quarter
        "ethical_flags": 0              # == 0 unresolved
    }

    def __init__(self):
        self.settings = get_settings()
        self.human_oversight = HumanOversightInterface()
        self._slm_service = None
        self._running = False
        self._reviews: List[QuarterlyReview] = []

    def _get_slm_service(self):
        """Lazy import SLM service"""
        if self._slm_service is None:
            from src.ai.slm.service import SLMService
            self._slm_service = SLMService()
        return self._slm_service

    async def get_current_metrics(self) -> SystemMetrics:
        """
        Fetch current system metrics from all services.

        In production, this would call each service's health/stats endpoint.
        """
        # Placeholder metrics - in production, fetch from services
        return SystemMetrics(
            ontologies_integrated=0,
            mmo_prediction_r2=0.0,
            task_success_rate=0.0,
            human_interventions_last_quarter=0,
            unresolved_ethical_alerts=len(self.human_oversight.get_unresolved_alerts()),
            total_roots=0,
            total_causality_links=0,
            avg_import_time_ms=0.0,
            slm_availability=1.0,
            storage_usage_percent=0.0
        )

    def evaluate_goals(self, metrics: SystemMetrics) -> StrategicGoals:
        """Evaluate which strategic goals are met"""
        return StrategicGoals(
            ontology_coverage=metrics.ontologies_integrated >= self.GOALS["ontology_coverage"],
            mmo_accuracy=metrics.mmo_prediction_r2 >= self.GOALS["mmo_accuracy"],
            ai_task_success=metrics.task_success_rate >= self.GOALS["ai_task_success"],
            human_intervention=metrics.human_interventions_last_quarter <= self.GOALS["human_intervention"],
            ethical_flags=metrics.unresolved_ethical_alerts == self.GOALS["ethical_flags"]
        )

    def identify_gaps(self, metrics: SystemMetrics, goals: StrategicGoals) -> List[str]:
        """Identify gaps between current state and goals"""
        gaps = []

        if not goals.ontology_coverage:
            gaps.append(f"ontology_coverage: {metrics.ontologies_integrated}/{self.GOALS['ontology_coverage']}")

        if not goals.mmo_accuracy:
            gaps.append(f"mmo_accuracy: {metrics.mmo_prediction_r2:.2f}/{self.GOALS['mmo_accuracy']}")

        if not goals.ai_task_success:
            gaps.append(f"ai_task_success: {metrics.task_success_rate:.2f}/{self.GOALS['ai_task_success']}")

        if not goals.human_intervention:
            gaps.append(f"human_intervention: {metrics.human_interventions_last_quarter}/{self.GOALS['human_intervention']}")

        if not goals.ethical_flags:
            gaps.append(f"unresolved_ethical_alerts: {metrics.unresolved_ethical_alerts}")

        return gaps

    async def generate_strategic_plan(
        self,
        metrics: SystemMetrics,
        gaps: List[str]
    ) -> StrategicPlan:
        """
        Generate strategic plan using SLM.

        v10 spec: Returns JSON plan with actions, rationale, rollback_plan
        """
        slm_service = self._get_slm_service()

        metrics_dict = {
            "ontologies_integrated": metrics.ontologies_integrated,
            "mmo_prediction_r2": metrics.mmo_prediction_r2,
            "task_success_rate": metrics.task_success_rate,
            "human_interventions_last_quarter": metrics.human_interventions_last_quarter,
            "unresolved_ethical_alerts": metrics.unresolved_ethical_alerts
        }

        plan_dict = await slm_service.generate_strategic_plan(
            metrics=metrics_dict,
            gaps=gaps
        )

        return StrategicPlan(
            actions=plan_dict.get("actions", []),
            rationale=plan_dict.get("rationale", ""),
            rollback_plan=plan_dict.get("rollback_plan", "Revert to previous state"),
            requires_human_approval=plan_dict.get("requires_human_approval", False),
            affected_components=plan_dict.get("affected_components", [])
        )

    async def implement_plan(self, plan: StrategicPlan) -> bool:
        """
        Implement approved strategic plan.

        Returns True if successful.
        """
        logger.info(f"Implementing strategic plan with {len(plan.actions)} actions")

        for action in plan.actions:
            logger.info(f"Executing: {action}")
            # In production, this would dispatch to appropriate services
            # For now, just log the actions

        return True

    async def evaluate_strategic_goals_quarterly(self):
        """
        v10 Phase 5: Full Implementation of Quarterly Strategic Review

        This is the main autonomous control loop that:
        1. Evaluates current metrics against goals
        2. Identifies gaps
        3. Generates strategic recommendations via SLM
        4. Requests human approval for critical changes
        5. Implements approved changes
        6. Runs quarterly (every 90 days)
        """
        self._running = True
        quarter_seconds = 90 * 86400  # 90 days

        while self._running:
            # Check for halt signal
            if self.human_oversight.check_halt_signal():
                logger.info("Strategic AI halted by human oversight")
                await asyncio.sleep(60)  # Check again in 1 minute
                continue

            try:
                # Step 1: Get current metrics
                current = await self.get_current_metrics()

                # Step 2: Evaluate goals
                goals = self.evaluate_goals(current)

                # Step 3: Identify gaps
                gaps = self.identify_gaps(current, goals)

                # Step 4: Generate plan via SLM
                plan = await self.generate_strategic_plan(current, gaps)

                # Step 5: Create review record
                review = QuarterlyReview(
                    review_id=generate_operation_id(),
                    timestamp=datetime.utcnow(),
                    current_metrics={
                        "ontologies_integrated": current.ontologies_integrated,
                        "mmo_prediction_r2": current.mmo_prediction_r2,
                        "task_success_rate": current.task_success_rate,
                        "human_interventions": current.human_interventions_last_quarter,
                        "ethical_alerts": current.unresolved_ethical_alerts
                    },
                    goals_met=goals,
                    gaps=gaps,
                    plan=plan,
                    status="pending"
                )

                self._reviews.append(review)

                # Step 6: v10 Safety - Check if plan affects root/causality
                critical_keywords = ["root", "causality", "mmo weight"]
                needs_approval = any(
                    any(kw in action.lower() for kw in critical_keywords)
                    for action in plan.actions
                )

                if needs_approval or plan.requires_human_approval:
                    # Request human approval
                    approved = await self.human_oversight.request_approval(plan)

                    if approved:
                        review.status = "approved"
                        await self.implement_plan(plan)
                        review.status = "implemented"
                    else:
                        review.status = "pending_approval"
                        logger.info("Plan pending human approval")
                else:
                    # Auto-implement non-critical changes
                    review.status = "approved"
                    await self.implement_plan(plan)
                    review.status = "implemented"

                logger.info(f"Quarterly review completed: {review.review_id}")
                logger.info(f"Goals met: {sum([goals.ontology_coverage, goals.mmo_accuracy, goals.ai_task_success, goals.human_intervention, goals.ethical_flags])}/5")

            except Exception as e:
                logger.error(f"Strategic evaluation failed: {e}")

            # Wait for next quarter (or shorter interval for testing)
            await asyncio.sleep(quarter_seconds)

    async def run_immediate_review(self) -> QuarterlyReview:
        """Run an immediate strategic review (for testing/manual trigger)"""
        current = await self.get_current_metrics()
        goals = self.evaluate_goals(current)
        gaps = self.identify_gaps(current, goals)
        plan = await self.generate_strategic_plan(current, gaps)

        review = QuarterlyReview(
            review_id=generate_operation_id(),
            timestamp=datetime.utcnow(),
            current_metrics={
                "ontologies_integrated": current.ontologies_integrated,
                "mmo_prediction_r2": current.mmo_prediction_r2,
                "task_success_rate": current.task_success_rate,
                "human_interventions": current.human_interventions_last_quarter,
                "ethical_alerts": current.unresolved_ethical_alerts
            },
            goals_met=goals,
            gaps=gaps,
            plan=plan,
            status="completed"
        )

        self._reviews.append(review)
        return review

    def stop(self):
        """Stop the strategic evaluation loop"""
        self._running = False

    def get_reviews(self) -> List[QuarterlyReview]:
        """Get all quarterly reviews"""
        return self._reviews

    def get_oversight_status(self) -> Dict[str, Any]:
        """Get current human oversight status"""
        return {
            "pending_approvals": len(self.human_oversight.get_pending_approvals()),
            "unresolved_alerts": len(self.human_oversight.get_unresolved_alerts()),
            "halt_active": self.human_oversight.check_halt_signal()
        }
