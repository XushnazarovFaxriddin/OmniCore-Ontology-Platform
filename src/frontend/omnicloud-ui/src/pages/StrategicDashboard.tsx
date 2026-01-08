
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { strategicApi } from '../api/client';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import type { QuarterlyReview, StrategicPlan, StrategicGoals } from '../types';

function StrategicDashboard() {
    const queryClient = useQueryClient();

    // Fetch Reviews
    const {
        data: reviews,
        isLoading: loadingReviews,
        error: reviewsError
    } = useQuery({
        queryKey: ['strategicReviews'],
        queryFn: strategicApi.getReviews,
    });

    // Fetch Oversight Status
    const {
        data: oversight,
        isLoading: loadingOversight,
        refetch: refetchOversight
    } = useQuery({
        queryKey: ['strategicOversight'],
        queryFn: strategicApi.getOversight,
        refetchInterval: 10000,
    });

    // Mutation to trigger review
    const triggerReviewMutation = useMutation({
        mutationFn: strategicApi.triggerReview,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['strategicReviews'] });
            alert('Strategic Review triggered successfully!');
        },
        onError: (err) => {
            alert('Failed to trigger review: ' + err);
        }
    });

    if (loadingReviews || loadingOversight) return <Loading />;
    if (reviewsError) return <ErrorMessage message="Failed to load strategic data" />;

    const latestReview = reviews && reviews.length > 0 ? reviews[reviews.length - 1] : null;

    return (
        <div className="strategic-dashboard">
            <div className="page-header">
                <h1 className="page-title">Strategic Meta-AI Dashboard</h1>
                <p className="page-subtitle">Autonomous strategic planning and human oversight interface</p>
            </div>

            {/* Oversight Status Card */}
            <div className="card" style={{ borderLeft: '4px solid var(--primary-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <h3 className="card-title">Human Oversight Status</h3>
                        <div style={{ display: 'flex', gap: '24px', marginTop: '16px' }}>
                            <StatusMetric
                                label="Pending Approvals"
                                value={oversight?.pending_approvals || 0}
                                color={oversight?.pending_approvals ? 'var(--warning-color)' : 'var(--success-color)'}
                            />
                            <StatusMetric
                                label="Unresolved Alerts"
                                value={oversight?.unresolved_alerts || 0}
                                color={oversight?.unresolved_alerts ? 'var(--danger-color)' : 'var(--success-color)'}
                            />
                            <StatusMetric
                                label="System Halt"
                                value={oversight?.halt_active ? "ACTIVE" : "INACTIVE"}
                                color={oversight?.halt_active ? 'var(--danger-color)' : 'var(--text-secondary)'}
                            />
                        </div>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={() => triggerReviewMutation.mutate()}
                        disabled={triggerReviewMutation.isPending}
                    >
                        {triggerReviewMutation.isPending ? 'Running Evaluation...' : 'Trigger Immediate Review'}
                    </button>
                </div>
            </div>

            {/* Latest Strategic Plan */}
            {latestReview ? (
                <div className="card" style={{ marginTop: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h3 className="card-title">Current Strategic Plan</h3>
                        <span style={{ color: 'var(--text-secondary)' }}>
                            Review ID: {latestReview.review_id.substring(0, 8)} |
                            Date: {new Date(latestReview.timestamp).toLocaleDateString()}
                        </span>
                    </div>

                    <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                        <div>
                            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                                Strategic Goals Status
                            </h4>
                            <GoalsList goals={latestReview.goals_met} />

                            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '24px', marginBottom: '8px' }}>
                                Identified Gaps
                            </h4>
                            <ul style={{ paddingLeft: '20px' }}>
                                {latestReview.gaps.map((gap, i) => (
                                    <li key={i} style={{ color: 'var(--danger-color)' }}>{gap}</li>
                                ))}
                                {latestReview.gaps.length === 0 && <li style={{ color: 'var(--success-color)' }}>No strategic gaps identified</li>}
                            </ul>
                        </div>

                        <div style={{ background: 'rgba(0,0,0,0.02)', padding: '16px', borderRadius: '8px' }}>
                            <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                                Proposed Actions (Plan)
                            </h4>
                            <ul style={{ paddingLeft: '20px', marginBottom: '16px' }}>
                                {latestReview.plan.actions.map((action, i) => (
                                    <li key={i} style={{ marginBottom: '8px' }}>{action}</li>
                                ))}
                            </ul>
                            <div style={{ fontSize: '13px' }}>
                                <strong>Rationale:</strong>
                                <p style={{ marginTop: '4px', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                                    {latestReview.plan.rationale}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="card" style={{ marginTop: '24px', textAlign: 'center', padding: '40px' }}>
                    <p style={{ color: 'var(--text-secondary)' }}>No strategic reviews found. Trigger a review to generate a plan.</p>
                </div>
            )}

            {/* History Table (Simplified) */}
            <h3 style={{ margin: '32px 0 16px', fontSize: '18px' }}>Review History</h3>
            <div className="table-container">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>ID</th>
                            <th>Status</th>
                            <th>Actions Proposed</th>
                            <th>Goals Met</th>
                        </tr>
                    </thead>
                    <tbody>
                        {(reviews || []).slice().reverse().map((review) => (
                            <tr key={review.review_id}>
                                <td>{new Date(review.timestamp).toLocaleDateString()}</td>
                                <td style={{ fontFamily: 'monospace' }}>{review.review_id.substring(0, 8)}</td>
                                <td><StatusBadge status={review.status} /></td>
                                <td>{review.plan.actions.length}</td>
                                <td>{Object.values(review.goals_met).filter(Boolean).length} / 5</td>
                            </tr>
                        ))}
                        {(!reviews || reviews.length === 0) && (
                            <tr>
                                <td colSpan={5} style={{ textAlign: 'center' }}>No reviews recorded</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function StatusMetric({ label, value, color }: { label: string, value: string | number, color: string }) {
    return (
        <div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color }}>{value}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {label}
            </div>
        </div>
    );
}

function GoalsList({ goals }: { goals: StrategicGoals }) {
    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
            <GoalItem label="Ontology Coverage (>= 1000)" met={goals.ontology_coverage} />
            <GoalItem label="MMO Accuracy (>= 0.90)" met={goals.mmo_accuracy} />
            <GoalItem label="AI Task Success (>= 0.92)" met={goals.ai_task_success} />
            <GoalItem label="Human Intervention (<= 20)" met={goals.human_intervention} />
            <GoalItem label="Ethical Compliance" met={goals.ethical_flags} />
        </div>
    );
}

function GoalItem({ label, met }: { label: string, met: boolean }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px' }}>
            <span style={{ color: met ? 'var(--success-color)' : 'var(--text-muted)' }}>
                {met ? '✓' : '○'}
            </span>
            <span style={{ color: met ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                {label}
            </span>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    let color = 'var(--text-secondary)';
    if (status === 'implemented' || status === 'completed') color = 'var(--success-color)';
    if (status === 'pending') color = 'var(--warning-color)';
    if (status === 'rejected') color = 'var(--danger-color)';

    return (
        <span style={{
            padding: '2px 8px',
            borderRadius: '4px',
            border: `1px solid ${color}`,
            color: color,
            fontSize: '12px',
            textTransform: 'uppercase'
        }}>
            {status}
        </span>
    );
}

export default StrategicDashboard;
