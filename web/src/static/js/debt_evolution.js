// Initialize the debt evolution chart when the page loads
document.addEventListener("DOMContentLoaded", function() {
    if (typeof debtData !== 'undefined' && debtData.length > 0) {
        createDebtEvolutionChart();
        createComplexityEvolutionChart();
        createDuplicationEvolutionChart();
        updateSummaryStats();
    }
});

function createDebtEvolutionChart() {
    // Process the data to create separate traces for each entity type
    const entityTypes = getUniqueEntityTypes();
    const traces = [];
    
    // Define colors for different entity types
    const colorPalette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ];

    entityTypes.forEach((entityType, index) => {
        const dates = [];
        const counts = [];
        
        debtData.forEach(commit => {
            dates.push(new Date(commit.commit_date));
            counts.push(commit.entity_breakdown[entityType] || 0);
        });
        
        traces.push({
            x: dates,
            y: counts,
            mode: 'lines+markers',
            name: entityType.toUpperCase(),
            line: {
                color: colorPalette[index % colorPalette.length],
                width: 2
            },
            marker: {
                size: 6,
                color: colorPalette[index % colorPalette.length]
            },
            hovertemplate: 
                '<b>%{fullData.name}</b><br>' +
                'Date: %{x}<br>' +
                'Count: %{y}<br>' +
                '<extra></extra>'
        });
    });

    // Chart layout
    const layout = {
        title: {
            text: `Technical Debt Evolution - ${repositoryName}`,
            font: { size: 18 }
        },
        xaxis: {
            title: 'Commit Date',
            type: 'date',
            tickformat: '%Y-%m-%d',
            tickangle: -45
        },
        yaxis: {
            title: 'Number of Identifiable Entities',
            rangemode: 'tozero'
        },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: 'rgba(0,0,0,0.2)',
            borderwidth: 1
        },
        hovermode: 'x unified',
        showlegend: true,
        plot_bgcolor: 'rgba(240,240,240,0.3)',
        paper_bgcolor: 'white',
        margin: {
            l: 60,
            r: 30,
            t: 60,
            b: 80
        }
    };

    // Chart configuration
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: `debt_evolution_${repositoryName.replace('/', '_')}`,
            height: 600,
            width: 1200,
            scale: 1
        }
    };

    // Create the chart
    Plotly.newPlot('debt-evolution-chart', traces, layout, config);
}

function createComplexityEvolutionChart() {
    // Prepare data for complexity chart
    const dates = [];
    const averageComplexity = [];
    
    debtData.forEach(commit => {
        dates.push(new Date(commit.commit_date));
        const complexityData = commit.complexity_data || {};
        averageComplexity.push(complexityData.average_complexity || 0);
    });

    // Create trace for average complexity only
    const traces = [
        {
            x: dates,
            y: averageComplexity,
            mode: 'lines+markers',
            name: 'Average Complexity',
            line: {
                color: '#4ecdc4',
                width: 2
            },
            marker: {
                size: 6,
                color: '#4ecdc4'
            },
            hovertemplate: 
                '<b>Average Complexity</b><br>' +
                'Date: %{x}<br>' +
                'Value: %{y:.2f}<br>' +
                '<extra></extra>'
        }
    ];

    // Chart layout with single y-axis
    const layout = {
        title: {
            text: `Average Complexity Evolution - ${repositoryName}`,
            font: { size: 18 }
        },
        xaxis: {
            title: 'Commit Date',
            type: 'date',
            tickformat: '%Y-%m-%d',
            tickangle: -45
        },
        yaxis: {
            title: 'Average Complexity',
            rangemode: 'tozero'
        },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: 'rgba(0,0,0,0.2)',
            borderwidth: 1
        },
        hovermode: 'x unified',
        showlegend: true,
        plot_bgcolor: 'rgba(240,240,240,0.3)',
        paper_bgcolor: 'white',
        margin: {
            l: 60,
            r: 30,
            t: 60,
            b: 80
        }
    };

    // Chart configuration
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: `complexity_evolution_${repositoryName.replace('/', '_')}`,
            height: 600,
            width: 1200,
            scale: 1
        }
    };

    // Create the chart
    Plotly.newPlot('complexity-evolution-chart', traces, layout, config);
}

function createDuplicationEvolutionChart() {
    // Prepare data for duplication chart
    const dates = [];
    const duplicated_instances = [];
    
    debtData.forEach(commit => {
        dates.push(new Date(commit.commit_date));
        const dupCount = commit.total_number_duplications || 0;
        duplicated_instances.push(dupCount);
    });

    const traces = [
        {
            x: dates,
            y: duplicated_instances,
            mode: 'lines+markers',
            name: 'Duplicate Fragments',
            line: {
                color: '#ff6b6b',
                width: 2
            },
            marker: {
                size: 6,
                color: '#ff6b6b'
            },
            hovertemplate: 
                '<b>Duplicate Fragments</b><br>' +
                'Date: %{x}<br>' +
                'Count: %{y}<br>' +
                '<extra></extra>'
        }
    ];

    // Chart layout
    const layout = {
        title: {
            text: `Code Duplication Evolution - ${repositoryName}`,
            font: { size: 18 }
        },
        xaxis: {
            title: 'Commit Date',
            type: 'date',
            tickformat: '%Y-%m-%d',
            tickangle: -45
        },
        yaxis: {
            title: 'Number of Duplicate Code Instances',
            rangemode: 'tozero',
            side: 'left'
        },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: 'rgba(0,0,0,0.2)',
            borderwidth: 1
        },
        hovermode: 'x unified',
        showlegend: true,
        plot_bgcolor: 'rgba(240,240,240,0.3)',
        paper_bgcolor: 'white',
        margin: {
            l: 60,
            r: 60,
            t: 60,
            b: 80
        }
    };

    // Chart configuration
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: `duplication_evolution_${repositoryName.replace('/', '_')}`,
            height: 600,
            width: 1200,
            scale: 1
        }
    };

    // Create the chart
    Plotly.newPlot('duplication-evolution-chart', traces, layout, config);
}

function getUniqueEntityTypes() {
    const entityTypesSet = new Set();
    
    debtData.forEach(commit => {
        Object.keys(commit.entity_breakdown).forEach(entityType => {
            entityTypesSet.add(entityType);
        });
    });
    
    return Array.from(entityTypesSet).sort();
}

function updateSummaryStats() {
    if (debtData.length === 0) return;
    // Calculate statistics
    const totalCommits = debtData.length;
    const totalDebts = debtData.map(commit => commit.total_identifiable_entities);
    const maxDebt = Math.max(...totalDebts);
    const currentDebt = totalDebts[totalDebts.length - 1];
    const linkedBugsTotal = (debtData[1] && debtData[1].linked_bugs_total); 
    
    // Calculate trend
    let trend = "No Change";
    let trendClass = "text-muted";
    
    if (totalDebts.length >= 2) {
        const firstDebt = totalDebts[0];
        const lastDebt = totalDebts[totalDebts.length - 1];
        
        if (lastDebt > firstDebt) {
            trend = "Increasing";
            trendClass = "text-danger";
        } else if (lastDebt < firstDebt) {
            trend = "Decreasing";
            trendClass = "text-success";
        }
    }
    
    // Update the DOM
    document.getElementById('total-commits').textContent = totalCommits;
    document.getElementById('linked-bugs-total').textContent = linkedBugsTotal;
    document.getElementById('max-debt').textContent = maxDebt;
    document.getElementById('current-debt').textContent = currentDebt;
    
    const trendElement = document.getElementById('debt-trend');
    trendElement.textContent = trend;
    trendElement.className = trendClass;
}

// Optional: Add chart interaction handlers
function addChartInteractions() {
    const chartDiv = document.getElementById('debt-evolution-chart');
    
    // Handle point clicks to show commit details
    chartDiv.on('plotly_click', function(data) {
        const pointIndex = data.points[0].pointIndex;
        const commit = debtData[pointIndex];
        
        if (commit) {
            // Show modal or tooltip with commit details
            showCommitDetails(commit);
        }
    });
}

function showCommitDetails(commit) {
    // Create a simple alert with commit details (you can replace with a modal)
    const details = `
        Commit: ${commit.commit_sha.substring(0, 8)}
        Author: ${commit.commit_author}
        Date: ${new Date(commit.commit_date).toLocaleDateString()}
        Message: ${commit.commit_message.substring(0, 100)}${commit.commit_message.length > 100 ? '...' : ''}
        Total Debt: ${commit.total_identifiable_entities}
    `;
    
    alert(details);
}