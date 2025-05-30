"""Cluster Analysis UI Module

Handles the display and interaction for facial cluster analysis.
Modularizes the cluster analysis components from the main interface.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from data_filters import DataFilters
from session_state_manager import SessionStateManager


class ClusterAnalysisUI:
    """Manages the cluster analysis user interface."""
    
    @staticmethod
    def render_feature_analysis():
        """Render the feature analysis interface with cluster analysis."""
        st.subheader("🔬 Facial Cluster Movement Analysis")
        
        if not SessionStateManager.has('frames_data') or SessionStateManager.get('frames_data') is None:
            st.info("📊 Create an animation first to analyze facial cluster movements.")
            st.markdown("""
            **Available Analysis Features:**
            - Individual cluster movement analysis
            - Cluster group comparisons  
            - Movement pattern visualization
            - Statistical summaries per cluster
            """)
            return
        
        # Run cluster analysis
        if st.button("📊 Analyze Facial Cluster Movements", type="primary", use_container_width=True):
            with st.spinner("Analyzing facial clusters..."):
                cluster_results = DataFilters.analyze_all_clusters(SessionStateManager.get('frames_data'))
                SessionStateManager.set('cluster_analysis', cluster_results)
                SessionStateManager.set('show_cluster_analysis', True)
        
        # Display cluster analysis results
        if SessionStateManager.has('show_cluster_analysis') and SessionStateManager.get('show_cluster_analysis'):
            cluster_results = SessionStateManager.get('cluster_analysis')
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Individual Clusters", "Cluster Groups", "Movement Patterns"])
            
            with tab1:
                ClusterAnalysisUI._render_individual_clusters(cluster_results)
            
            with tab2:
                ClusterAnalysisUI._render_cluster_groups(cluster_results)
            
            with tab3:
                ClusterAnalysisUI._render_movement_patterns(cluster_results)
    
    @staticmethod
    def _render_individual_clusters(cluster_results: Dict[str, Any]):
        """Render individual cluster analysis."""
        st.write("### Movement by Individual Facial Clusters")
        
        # Sort clusters by total movement
        sorted_clusters = sorted(
            [(k, v) for k, v in cluster_results.items() if not k.startswith('GROUP_')],
            key=lambda x: x[1]['total_movement'],
            reverse=True
        )
        
        # Display top movers
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Most Active Clusters:**")
            for i, (name, stats) in enumerate(sorted_clusters[:10]):
                st.write(f"{i+1}. **{name}**: {stats['total_movement']:.2f} total movement")
                st.write(f"   - Mean: {stats['mean_movement']:.4f}")
                st.write(f"   - Max: {stats['max_movement']:.4f}")
        
        with col2:
            st.write("**Least Active Clusters:**")
            for i, (name, stats) in enumerate(sorted_clusters[-10:][::-1]):
                st.write(f"{i+1}. **{name}**: {stats['total_movement']:.2f} total movement")
                st.write(f"   - Mean: {stats['mean_movement']:.4f}")
                st.write(f"   - Max: {stats['max_movement']:.4f}")
    
    @staticmethod
    def _render_cluster_groups(cluster_results: Dict[str, Any]):
        """Render cluster group analysis."""
        st.write("### Movement by Cluster Groups")
        
        # Get group results
        group_results = [(k, v) for k, v in cluster_results.items() if k.startswith('GROUP_')]
        sorted_groups = sorted(group_results, key=lambda x: x[1]['total_movement'], reverse=True)
        
        if sorted_groups:
            # Create bar chart data
            group_data = pd.DataFrame([
                {
                    'Group': name.replace('GROUP_', ''),
                    'Total Movement': stats['total_movement'],
                    'Mean Movement': stats['mean_movement'],
                    'Landmarks': stats['num_landmarks']
                }
                for name, stats in sorted_groups
            ])
            
            st.bar_chart(group_data.set_index('Group')['Total Movement'])
            
            # Display detailed stats
            for name, stats in sorted_groups:
                group_name = name.replace('GROUP_', '')
                with st.expander(f"📊 {group_name.title()} Details"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Movement", f"{stats['total_movement']:.2f}")
                    with col2:
                        st.metric("Mean Movement", f"{stats['mean_movement']:.4f}")
                    with col3:
                        st.metric("Landmarks", stats['num_landmarks'])
        else:
            st.info("No cluster group data available.")
    
    @staticmethod
    def _render_movement_patterns(cluster_results: Dict[str, Any]):
        """Render movement pattern analysis."""
        st.write("### Movement Pattern Analysis")
        
        # Show movement statistics summary
        all_movements = [stats['total_movement'] for stats in cluster_results.values() 
                       if not stats.get('cluster_name', '').startswith('GROUP_')]
        
        if all_movements:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clusters", len(all_movements))
            with col2:
                st.metric("Mean Movement", f"{np.mean(all_movements):.2f}")
            with col3:
                st.metric("Max Movement", f"{np.max(all_movements):.2f}")
            with col4:
                st.metric("Movement Std Dev", f"{np.std(all_movements):.2f}")
            
            # Movement distribution
            st.write("**Movement Distribution:**")
            movement_df = pd.DataFrame({
                'Cluster': [k for k in cluster_results.keys() if not k.startswith('GROUP_')],
                'Movement': [v['total_movement'] for k, v in cluster_results.items() if not k.startswith('GROUP_')]
            })
            st.bar_chart(movement_df.set_index('Cluster')['Movement'])
        else:
            st.info("No movement pattern data available.") 