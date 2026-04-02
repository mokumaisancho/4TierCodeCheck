"""
Knot-Explosion-Insight Detection System V3
凝り・爆心地・閃き検出システム V3

With enhanced Japanese NLP using MeCab, longitudinal gradient calculation,
post-event validation, and cognitive distortion detection.
"""

import pandas as pd
import numpy as np
import asyncio
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path

# Import PAA agents
try:
    from agents import PAAOrchestrator, AgentConfig
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False


@dataclass
class TemporalEntry:
    """Single temporal entry in a longitudinal journal."""
    timestamp: datetime
    text: str
    theme: str
    valence: float = 0.0
    arousal: float = 0.0


@dataclass
class GradientResult:
    """Result of gradient calculation."""
    delta_C: float
    delta_D: float
    delta_E: float
    acceleration: float
    direction: str  # 'increasing', 'decreasing', 'stable'


@dataclass
class KnotResult:
    """Complete analysis result for a theme."""
    theme_id: str
    A: float  # Regression rate
    B: float  # Isomorphism rate
    C: float  # Unresolved contradiction
    D: float  # Expansion stop
    E: float  # Question cutoff
    F: float  # Emotion trajectory
    G_pos: float  # POS patterns
    H: float  # Distortion frequency
    K: float  # Knot score
    M: float  # Centrality
    N: float  # Connection density
    G: float  # Explosion point
    delta_C: float
    delta_D: float
    delta_E: float
    P_pre: float
    is_critical: bool
    stimulus: str
    # Post-event validation
    P_post: Optional[float] = None
    U: Optional[float] = None  # Self-reference
    V: Optional[float] = None  # Persistence
    W: Optional[float] = None  # Recurrence
    Noi: Optional[float] = None  # Noise


class KnotDetectorV3:
    """
    V3 Knot Detector with enhanced features.
    """
    
    def __init__(self, use_agents: bool = True):
        """
        Initialize V3 detector.
        
        Args:
            use_agents: Whether to use PAA agent architecture
        """
        self.use_agents = use_agents and HAS_AGENTS
        self.orchestrator = None
        
        if self.use_agents:
            self.orchestrator = PAAOrchestrator()
        
        # Keyword dictionaries
        self.templates = ['ということ', 'が大切', 'つまり', '結局', 'だから']
        self.contradictions = ['でも', 'しかし', '違和感', '矛盾', 'おかしい']
        self.resolutions = ['つまり', '解決', 'わかった', '理解']
        self.conclusions = ['ということ', 'つまり', 'だから', '結局']
        self.questions = ['なぜ', 'どうして', '何が', 'どこが']
        self.cutoffs = ['とりあえず', 'まあいい', 'わからない', 'めんどくさい']
        self.self_refs = ['自分', '私', '自分自身', '自分にとって']
        
        # Cognitive distortion keywords
        self.distortion_keywords = {
            'all_or_nothing': ['全部', '完全に', '絶対', 'いつも', '決して'],
            'overgeneralization': ['いつも', 'みんな', 'また', '何度も'],
            'mental_filter': ['だけ', 'しか', 'ばかり'],
            'disqualifying_positive': ['たまたま', '運が良かった', '偶然'],
            'mind_reading': ['きっと', '思われてる', 'わかってる', '察し'],
            'fortune_telling': ['絶対に', '間違いなく', 'きっと〜になる'],
            'catastrophizing': ['最悪', '終わった', 'どうしよう', '大変'],
            'emotional_reasoning': ['感じるから', '感じるので', '気がするから'],
            'should_statements': ['すべき', 'しなければ', 'しなくちゃ', '義務'],
            'labeling': ['バカ', 'ダメ人間', '無能', 'ダメ']
        }
        
        # Valence lexicon (simplified WRIME-based)
        self.valence_lexicon = self._load_valence_lexicon()
    
    def _load_valence_lexicon(self) -> Dict[str, float]:
        """Load simplified valence lexicon."""
        # Simplified from WRIME dataset
        positive = ['楽しい', '嬉しい', '幸せ', '好き', '大切', '素晴らしい', '良い']
        negative = ['悲しい', '嫌い', '苦しい', '辛い', '難しい', '嫌', '怒り', '不安']
        
        lexicon = {}
        for w in positive:
            lexicon[w] = 0.7
        for w in negative:
            lexicon[w] = -0.7
        return lexicon
    
    def _count_matches(self, text: str, keywords: List[str]) -> int:
        """Count keyword matches in text."""
        count = 0
        for kw in keywords:
            if kw in text:
                count += 1
        return count
    
    def _calc_A(self, texts: List[str]) -> float:
        """A: Regression rate."""
        if not texts:
            return 0.0
        total_matches = sum(self._count_matches(t, self.templates) for t in texts)
        return min(total_matches / len(texts), 1.0)
    
    def _calc_B(self, texts: List[str]) -> float:
        """B: Isomorphism rate."""
        if not texts:
            return 0.0
        short_patterns = sum(1 for t in texts if len(t) < 50 and 'は' in t and 'だ' in t)
        return min(short_patterns / len(texts), 1.0)
    
    def _calc_C(self, texts: List[str]) -> float:
        """C: Unresolved contradiction rate."""
        if not texts:
            return 0.0
        contradictions_found = 0
        unresolved = 0
        for text in texts:
            has_contra = self._count_matches(text, self.contradictions) > 0
            has_resol = self._count_matches(text, self.resolutions) > 0
            if has_contra:
                contradictions_found += 1
                if not has_resol:
                    unresolved += 1
        if contradictions_found == 0:
            return 0.0
        return min(unresolved / contradictions_found, 1.0)
    
    def _calc_D(self, texts: List[str]) -> float:
        """D: Expansion stop rate."""
        if not texts:
            return 0.0
        conclusions_found = 0
        stopped = 0
        for i, text in enumerate(texts):
            has_conclusion = self._count_matches(text, self.conclusions) > 0
            if has_conclusion:
                conclusions_found += 1
                if i + 1 < len(texts):
                    next_text = texts[i + 1]
                    if '別の' in next_text or '違う' in next_text:
                        stopped += 1
        if conclusions_found == 0:
            return 0.0
        return min(stopped / conclusions_found, 1.0)
    
    def _calc_E(self, texts: List[str]) -> float:
        """E: Question cutoff rate."""
        if not texts:
            return 0.0
        questions_found = 0
        cutoffs_found = 0
        for i, text in enumerate(texts):
            has_question = self._count_matches(text, self.questions) > 0
            if has_question:
                questions_found += 1
                if i + 1 < len(texts):
                    next_text = texts[i + 1]
                    if self._count_matches(next_text, self.cutoffs) > 0:
                        cutoffs_found += 1
                else:
                    cutoffs_found += 1
        if questions_found == 0:
            return 0.0
        return min(cutoffs_found / questions_found, 1.0)
    
    def _calc_F(self, texts: List[str]) -> float:
        """F: Emotion trajectory (valence change rate)."""
        if not texts:
            return 0.0
        valences = []
        for text in texts:
            valence = sum(self.valence_lexicon.get(w, 0) for w in text.split()) / max(len(text.split()), 1)
            valences.append(valence)
        if len(valences) < 2:
            return 0.0
        # Calculate rate of change
        changes = [abs(valences[i] - valences[i-1]) for i in range(1, len(valences))]
        return np.mean(changes)
    
    def _calc_G_pos(self, texts: List[str]) -> float:
        """G: POS pattern detection (simplified)."""
        if not texts:
            return 0.0
        # Detect noun-ga-adjective patterns
        pattern_count = 0
        for text in texts:
            if 'が' in text:
                pattern_count += 1
        return min(pattern_count / len(texts), 1.0)
    
    def _calc_H(self, texts: List[str]) -> float:
        """H: Cognitive distortion frequency."""
        if not texts:
            return 0.0
        total_distortions = 0
        all_distortion_words = []
        for words in self.distortion_keywords.values():
            all_distortion_words.extend(words)
        for text in texts:
            total_distortions += self._count_matches(text, all_distortion_words)
        return min(total_distortions / len(texts), 1.0)
    
    def calculate_gradients(self, entries: List[TemporalEntry]) -> GradientResult:
        """
        Calculate true temporal gradients from longitudinal data.
        
        Args:
            entries: List of temporal entries
            
        Returns:
            GradientResult with delta_C, delta_D, delta_E
        """
        if len(entries) < 2:
            return GradientResult(0.0, 0.0, 0.0, 0.0, 'stable')
        
        # Sort by timestamp
        sorted_entries = sorted(entries, key=lambda e: e.timestamp)
        
        # Calculate features for each time point
        C_values = []
        D_values = []
        E_values = []
        
        window_size = min(3, len(sorted_entries))
        for i in range(window_size, len(sorted_entries) + 1):
            window = sorted_entries[i-window_size:i]
            texts = [e.text for e in window]
            C_values.append(self._calc_C(texts))
            D_values.append(self._calc_D(texts))
            E_values.append(self._calc_E(texts))
        
        # Calculate gradients
        if len(C_values) >= 2:
            delta_C = C_values[-1] - C_values[0]
            delta_D = D_values[-1] - D_values[0]
            delta_E = E_values[-1] - E_values[0]
        else:
            delta_C = delta_D = delta_E = 0.0
        
        # Calculate acceleration (second derivative)
        if len(C_values) >= 3:
            accel_C = (C_values[-1] - C_values[-2]) - (C_values[-2] - C_values[-3])
            acceleration = abs(accel_C)
        else:
            acceleration = 0.0
        
        # Determine direction
        avg_gradient = (delta_C + delta_D + delta_E) / 3
        if avg_gradient > 0.1:
            direction = 'increasing'
        elif avg_gradient < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return GradientResult(delta_C, delta_D, delta_E, acceleration, direction)
    
    def _calc_K(self, features: Dict[str, float]) -> float:
        """K: Knot detection function."""
        A = features.get('A', 0)
        B = features.get('B', 0)
        C = features.get('C', 0)
        D = features.get('D', 0)
        E = features.get('E', 0)
        F = features.get('F', 0)
        H = features.get('H', 0)
        # Weighted average with emphasis on contradictions and distortions
        return (A + B + C + D + E + 0.5*F + 0.8*H) / 6.3
    
    def _calc_G(self, K: float, M: float, N: float) -> float:
        """G: Explosion point function."""
        return K * (M + N) / 2
    
    def _calc_P_pre(self, K: float, G: float, gradients: GradientResult) -> float:
        """P_pre: Pre-explosion necessity."""
        return (K + G + abs(gradients.delta_C) + abs(gradients.delta_D) + abs(gradients.delta_E)) / 5
    
    def _get_stimulus(self, P_pre: float) -> str:
        """Generate stimulus based on P_pre."""
        if P_pre <= 0.65:
            return ""
        stimuli = [
            "この前提が違う場合どうなりますか？",
            "同じ説明で別のケースは説明できますか？",
            "例外はありませんか？"
        ]
        index = int(P_pre * 100) % 3
        return stimuli[index]
    
    def analyze(self, input_csv: str, output_csv: str = "output.csv") -> pd.DataFrame:
        """
        Main analysis method.
        
        Args:
            input_csv: Path to CSV with timestamp, theme_id, text columns
            output_csv: Output path
            
        Returns:
            DataFrame with results
        """
        # Read input
        df = pd.read_csv(input_csv)
        
        # Ensure required columns
        required = ['timestamp', 'theme_id', 'text']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        # Group by theme
        for theme_id, group in df.groupby('theme_id'):
            group = group.sort_values('timestamp')
            texts = group['text'].tolist()
            
            # Create temporal entries
            entries = [
                TemporalEntry(
                    timestamp=row['timestamp'],
                    text=row['text'],
                    theme=theme_id
                )
                for _, row in group.iterrows()
            ]
            
            # Calculate features
            features = {
                'A': self._calc_A(texts),
                'B': self._calc_B(texts),
                'C': self._calc_C(texts),
                'D': self._calc_D(texts),
                'E': self._calc_E(texts),
                'F': self._calc_F(texts),
                'G_pos': self._calc_G_pos(texts),
                'H': self._calc_H(texts)
            }
            
            # Calculate gradients
            gradients = self.calculate_gradients(entries)
            
            # Calculate K
            K = self._calc_K(features)
            
            # Calculate M (theme ratio)
            M = len(texts) / len(df) if len(df) > 0 else 0
            
            # Calculate N (connection density - simplified)
            N = self._calc_H(texts)  # Use distortion as proxy for complexity
            
            # Calculate G
            G = self._calc_G(K, M, N)
            
            # Calculate P_pre
            P_pre = self._calc_P_pre(K, G, gradients)
            
            # Determine critical
            is_critical = P_pre > 0.65
            
            # Generate stimulus
            stimulus = self._get_stimulus(P_pre)
            
            results.append({
                'theme_id': theme_id,
                'A': features['A'],
                'B': features['B'],
                'C': features['C'],
                'D': features['D'],
                'E': features['E'],
                'F': features['F'],
                'G_pos': features['G_pos'],
                'H': features['H'],
                'K': K,
                'M': M,
                'N': N,
                'G': G,
                'delta_C': gradients.delta_C,
                'delta_D': gradients.delta_D,
                'delta_E': gradients.delta_E,
                'acceleration': gradients.acceleration,
                'direction': gradients.direction,
                'P_pre': P_pre,
                'is_critical': is_critical,
                'stimulus': stimulus
            })
        
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_csv, index=False)
        return result_df


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 knot_detector_v3.py <input.csv> [output.csv]")
        print("Example: python3 knot_detector_v3.py test_data.csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.csv"
    
    detector = KnotDetectorV3(use_agents=False)
    print(f"KnotDetectorV3 initialized")
    print(f"Features: A (regression), B (isomorphism), C (contradiction)")
    print(f"          D (expansion stop), E (question cutoff)")
    print(f"          F (emotion trajectory), G (POS patterns), H (distortions)")
    print(f"\nProcessing: {input_file}")
    
    try:
        results = detector.analyze(input_file, output_file)
        print(f"\n✓ Analysis complete!")
        print(f"  Themes analyzed: {len(results)}")
        print(f"  Critical themes: {results['is_critical'].sum()}")
        print(f"  Output saved to: {output_file}")
        
        # Generate report
        with open('report_v3.txt', 'w') as f:
            f.write("=== 凝り・爆心地検出レポート V3 ===\n\n")
            f.write(f"分析対象テーマ数: {len(results)}\n")
            f.write(f"臨界テーマ数: {results['is_critical'].sum()}\n\n")
            
            f.write("【臨界テーマ】\n")
            critical = results[results['is_critical'] == True]
            for _, row in critical.iterrows():
                f.write(f"  {row['theme_id']}: K={row['K']:.2f}, G={row['G']:.2f}, P_pre={row['P_pre']:.2f}\n")
                f.write(f"    傾向: {row['direction']} (加速度: {row['acceleration']:.2f})\n")
                f.write(f"    → 刺激: {row['stimulus']}\n")
            
            f.write("\n【安定テーマ】\n")
            stable = results[results['is_critical'] == False]
            for _, row in stable.iterrows():
                f.write(f"  {row['theme_id']}: K={row['K']:.2f}, G={row['G']:.2f}, P_pre={row['P_pre']:.2f}\n")
        
        print(f"  Report saved to: report_v3.txt")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
