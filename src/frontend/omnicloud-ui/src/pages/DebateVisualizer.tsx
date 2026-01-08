
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { debateApi } from '../api/client';
import type { ConflictResolution, DebateRound } from '../types';

function DebateVisualizer() {
    const [topic, setTopic] = useState('');
    const [result, setResult] = useState<ConflictResolution | null>(null);

    const debateMutation = useMutation({
        mutationFn: debateApi.runDebate,
        onSuccess: (data) => {
            setResult(data);
        },
        onError: (err) => {
            alert('Debate failed: ' + err);
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic.trim()) return;
        debateMutation.mutate(topic);
    };

    return (
        <div className="debate-visualizer">
            <div className="page-header">
                <h1 className="page-title">Conflict Resolution Lab</h1>
                <p className="page-subtitle">Simulate philosophical debates between AI agents</p>
            </div>

            {/* Input Section */}
            <div className="card">
                <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px' }}>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Enter a concept to debate (e.g., 'The Number 2', 'Justice', 'Virus')"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        disabled={debateMutation.isPending}
                        style={{ flex: 1 }}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={debateMutation.isPending || !topic.trim()}
                    >
                        {debateMutation.isPending ? 'Debating...' : 'Start Debate'}
                    </button>
                </form>
            </div>

            {/* Debate Visualization */}
            {result && (
                <div className="debate-results" style={{ marginTop: '32px' }}>
                    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                        <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>Verdict: {result.final_resolution}</h2>
                        <div style={{ display: 'inline-block', padding: '4px 12px', background: result.consensus_reached ? 'var(--success-color)' : 'var(--warning-color)', borderRadius: '16px', color: 'white', fontSize: '14px', fontWeight: 'bold' }}>
                            {result.consensus_reached ? 'CONSENSUS REACHED' : 'NO CONSENSUS'}
                        </div>
                        {result.contextual_axiom && (
                            <div style={{ marginTop: '16px', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                                axiom: "{result.contextual_axiom}"
                            </div>
                        )}
                    </div>

                    <div className="timeline" style={{ position: 'relative', maxWidth: '800px', margin: '0 auto' }}>
                        {result.rounds.map((round, index) => (
                            <DebateCard key={index} round={round} />
                        ))}
                    </div>
                </div>
            )}

            {/* Loading State Animation */}
            {debateMutation.isPending && (
                <div style={{ textAlign: 'center', padding: '60px' }}>
                    <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
                    <p style={{ fontSize: '18px', color: 'var(--text-secondary)' }}>
                        Agents are deliberating...<br />
                        <span style={{ fontSize: '14px' }}>(Platonist, Nominalist, and Pragmatist are active)</span>
                    </p>
                </div>
            )}
        </div>
    );
}

function DebateCard({ round }: { round: DebateRound }) {
    const isLeft = round.agent_role === 'platonist' || round.agent_role === 'pragmatist';
    const color =
        round.agent_role === 'platonist' ? '#8b5cf6' :
            round.agent_role === 'nominalist' ? '#ef4444' :
                '#10b981'; // pragmatist

    return (
        <div style={{
            display: 'flex',
            justifyContent: isLeft ? 'flex-start' : 'flex-end',
            marginBottom: '24px'
        }}>
            <div style={{
                maxWidth: '70%',
                background: 'var(--card-bg)',
                border: '1px solid var(--border-color)',
                borderLeft: `4px solid ${color}`,
                borderRadius: '8px',
                padding: '16px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold', textTransform: 'capitalize', color }}>{round.agent_role}</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Round {round.round_number}</span>
                </div>
                <p style={{ lineHeight: '1.5' }}>{round.argument}</p>
                <div style={{ marginTop: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                    Confidence: {(round.confidence * 100).toFixed(0)}%
                </div>
            </div>
        </div>
    );
}

export default DebateVisualizer;
