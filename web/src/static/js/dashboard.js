// search container elements
const branch_select = document.getElementById("branch_select");
const commit_select = document.getElementById("commit_select");

const include_identifiable_identities_label = document.getElementById("include_identifiable_identities_label");
const include_identifiable_identities_input = document.getElementById("include_identifiable_identities_input");
const include_complexity_input = document.getElementById("include_complexity_input");
const include_duplication_input = document.getElementById("include_duplication_input");

// commit selected for metrics display
const commit_sha_display = document.getElementById("commit-sha");
const commit_date_display = document.getElementById("commit-date");
const commit_message_display = document.getElementById("commit-message");

let to_export_metrics = {};
let to_export_global_stats = {}

// once doc is ready
document.addEventListener("DOMContentLoaded", () => {
    // init the commits select
    const branch_id = get_selected_branch_id();
    get_commits_by_branch_id(branch_id).then((commits) => {
        set_commit_select_options(commits);
    });

    // refresh the list of commits when the user selects a new branch
    branch_select.addEventListener("change", () => {
        const branch_id = get_selected_branch_id();
        get_commits_by_branch_id(branch_id).then((commits) => {
            set_commit_select_options(commits);
        });
    });

    // init the identifiable identities list to show the users the ones he can select/deselect
    
    const identifiable_identities_list_tippy = tippy(include_identifiable_identities_label, {
        allowHTML: true,
        arrow: false,
        interactive: true,
        placement: "bottom",
        content: `
            
        `,
    });
    include_identifiable_identities_label.addEventListener("click", () => {
        identifiable_identities_list_tippy.show();
    });
});

function set_commit_select_options(commits) {
    console.log('Setting commit options, received commits:', commits);
    console.log('Number of commits:', commits ? commits.length : 0);
    
    commit_select.innerHTML = "";
    commits.forEach((commit) => {
        const { id, message } = commit;

        const container = document.createElement("option");
        container.setAttribute("data-id", id);
        const truncated = message.length > 150 ? message.slice(0, 150) + "..." : message;
        container.innerHTML = truncated;

        commit_select.appendChild(container);
    });
    
    console.log('Commit select now has', commit_select.options.length, 'options');
}

function display_metrics() {
    const branch_id = get_selected_branch_id();
    const commit_id = get_selected_commit_id();
    const include_identifiable_identities = include_identifiable_identities_input.checked;
    const include_complexity = include_complexity_input.checked;
    const include_duplication = include_duplication_input.checked;

    display_metrics_by_commit_id(repository_id, branch_id, commit_id, include_complexity, include_identifiable_identities, include_duplication).then((metrics) => {
        const { commit_date, commit_message, commit_sha, cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis } = metrics;
        render_commit_info(commit_sha, commit_date, commit_message);
        render_global_statistics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis);
        render_calculated_metrics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis);
        render_code_duplication(duplicated_code_analysis);
        render_files_recommendations(duplicated_code_analysis);
    });
}

function get_selected_branch_id() {
    return branch_select.options[branch_select.selectedIndex].getAttribute("data-id");
}

function get_selected_commit_id() {
    return commit_select.options[commit_select.selectedIndex].getAttribute("data-id");
}

// show the commit sha, date and message under the repo information selection
function render_commit_info(commit_sha, commit_date, commit_message) {
    commit_sha_display.textContent = commit_sha || "-";
    commit_date_display.textContent = commit_date || "-";
    commit_message_display.textContent = commit_message || "";
}

// Generate the total technical debt (all instances of duplicates + identifiable identities, and cylomatic complexity above 10)
function render_global_statistics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis) {
        function nb_high_risk_files(analysis) {
        if (!analysis || !Array.isArray(analysis)) {
            return 0;
        }

        let count = 0;
        const MEDIUM_RISK = 11;
        for(const file of analysis) {
            if (!Array.isArray(file)) {
                continue;
            }

            let sum = 0;
            file.forEach((funct, index) => sum += funct.cyclomatic_complexity);
            sum /= file.length;
            count = (sum >= MEDIUM_RISK) ? count + 1 : count;
        }

        return count;
    }

    function nb_duplications(analysis) {
        try {
            const duplication_dict = analysis["duplications"];
            let sum = 0;
            for(const key in duplication_dict) {
                const duplication_instances = duplication_dict[key]._files.length;
                sum += duplication_instances;
            }
            return sum;
        }
        catch (error) {
            return 0;
        }
    }

    let totalTechnicalDebt = 0;

    const totalHighRiskFiles = nb_high_risk_files(cyclomatic_complexity_analysis);
    totalTechnicalDebt += totalHighRiskFiles;

    const identifiableIdentitiesCount = identifiable_identities_analysis.length;
    totalTechnicalDebt += identifiableIdentitiesCount;

    const duplication_count = nb_duplications(duplicated_code_analysis);
    totalTechnicalDebt += duplication_count;

    // adds the global stats to the "to_export_data" object. 
    // used for exporting to JSON.
    to_export_global_stats = {
        "total_technical_debt": totalTechnicalDebt, 
        "high_risk_files": totalHighRiskFiles, 
        "__todo_fixme": identifiableIdentitiesCount, 
        "__duplications": duplication_count
    };

    document.getElementById("total-technical-debt").innerHTML = totalTechnicalDebt;
    document.getElementById("high-risk-files").innerHTML = totalHighRiskFiles;
    document.getElementById("--todo-fixme").innerHTML = identifiableIdentitiesCount;
    document.getElementById("--duplications").innerHTML = duplication_count;
}

function render_calculated_metrics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis) {
    // Process the data to group by file
    const fileMetrics = processMetricsData(
        cyclomatic_complexity_analysis, 
        identifiable_identities_analysis, 
        duplicated_code_analysis
    );

    // Initialize or refresh the table
    const $table = $('#metrics-table');
    
    // Destroy existing table if it exists
    if ($table.bootstrapTable('getOptions')) {
        $table.bootstrapTable('destroy');
    }

    // Initialize the table with data
    $table.bootstrapTable({
        columns: [
            {
                field: 'fileName',
                title: 'File Name',
                sortable: true,
                width: '40%'
            },
            {
                field: 'avgComplexity',
                title: 'Avg Complexity',
                sortable: true,
                align: 'center',
                width: '15%',
                formatter: (value) => value !== null ? value.toFixed(2) : '-'
            },
            {
                field: 'identifiableIdentitiesCount',
                title: 'Identifiable Identities',
                sortable: true,
                align: 'center',
                width: '15%'
            },
            {
                field: 'duplicateCodeCount',
                title: 'Duplicate Code',
                sortable: true,
                align: 'center',
                width: '15%'
            },
            {
                field: 'priorityScore',
                title: 'Priority Score',
                sortable: true,
                align: 'center',
                width: '15%'
            }
        ],
        data: fileMetrics,
        detailView: true,
        detailFormatter: detailFormatter,
        detailViewIcon: true,
        detailViewByClick: false,
        showColumns: false,
        onPostBody: function() {
            // Force visibility of detail icons
            $table.find('.detail-icon').css({
                'color': '#495057',
                'font-weight': 'bold',
                'font-size': '1.2rem'
            });
        }
    });
}

// Process metrics data to group by file
function processMetricsData(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis) {
    const fileMap = new Map();

    // Process cyclomatic complexity data
    if (cyclomatic_complexity_analysis && Array.isArray(cyclomatic_complexity_analysis)) {
        cyclomatic_complexity_analysis.forEach(fileArray => {
            if (Array.isArray(fileArray) && fileArray.length > 0) {
                const fileName = fileArray[0].file;
                
                createNewFileMapSet(fileMap, fileName);

                const fileData = fileMap.get(fileName);
                fileData.functions = fileArray.map(func => ({
                    name: func.function,
                    line: func.start_line,
                    complexity: func.cyclomatic_complexity
                }));

                // Calculate average complexity
                const totalComplexity = fileArray.reduce((sum, func) => sum + func.cyclomatic_complexity, 0);
                fileData.avgComplexity = totalComplexity / fileArray.length;
            }
        });
    }

    // Process identifiable identities data
    if (identifiable_identities_analysis && Array.isArray(identifiable_identities_analysis)) {
        identifiable_identities_analysis.forEach(entity => {
            const fileName = entity.file_name;
            
            createNewFileMapSet(fileMap, fileName);

            const fileData = fileMap.get(fileName);
            fileData.identifiableIdentitiesCount++;
        });
    }

    // Process duplicate code data
    if (duplicated_code_analysis !== undefined) {

        const duplicates = Object.values(duplicated_code_analysis["duplications"]);

        for (const duplicate of duplicates) {
            const files = duplicate["_files"];
            
            for (const file of files) {
                const fileName = file.filename;

                createNewFileMapSet(fileMap, fileName);

                const fileData = fileMap.get(fileName);
                fileData.duplicateCodeCount++;
            }
        }
    }

    // Process priority score data

    for(key of fileMap.keys()) {
        createNewFileMapSet(fileMap, key);
    }

    fileMap.forEach((value, key, map) => {
        const fileData = fileMap.get(key);
        fileData.priorityScore = (fileData.duplicateCodeCount + fileData.identifiableIdentitiesCount + fileData.avgComplexity).toFixed(2)
    })

    to_export_metrics = {
        "complexity": cyclomatic_complexity_analysis, 
        "todo_fixme": identifiable_identities_analysis,
        "duplication": duplicated_code_analysis["duplications"],
        "recommendation": duplicated_code_analysis["recommendations"], 
        "global_stats": {}
    }
    return Array.from(fileMap.values());
}

// Detail formatter for expandable rows
function detailFormatter(index, row) {

    if (!row.functions || row.functions.length === 0) {
        return '<div class="p-3 text-muted">No function data available</div>';
    }

    let html = '<div class="p-3"><table class="table table-sm table-striped">';
    html += '<thead><tr>';
    html += '<th style="width: 60%">Function Name</th>';
    html += '<th style="width: 20%" class="text-center">Line</th>';
    html += '<th style="width: 20%" class="text-center">Complexity</th>';
    html += '</tr></thead>';
    html += '<tbody>';

    row.functions.forEach(func => {
        html += '<tr>';
        html += `<td><code>${func.name}</code></td>`;
        html += `<td class="text-center">${func.line}</td>`;
        html += `<td class="text-center"><span class="badge ${getComplexityBadgeClass(func.complexity)}">${func.complexity}</span></td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    return html;
}

// Helper function to get badge color based on complexity
function getComplexityBadgeClass(complexity) {
    if (complexity <= 10) return 'bg-success';
    if (complexity <= 20) return 'bg-warning';
    return 'bg-danger';
}


// code duplication analysis
function render_code_duplication(duplicated_code_analysis) {
    // Initialize or refresh the table
    const $table = $('#duplication-table');
    
    // Destroy existing table if it exists
    if ($table.bootstrapTable('getOptions')) {
        $table.bootstrapTable('destroy');
    }

    // Check if duplicated_code_analysis exists and has duplications
    if (!duplicated_code_analysis || !duplicated_code_analysis["duplications"]) {
        // Initialize empty table if no data
        $table.bootstrapTable({
            columns: [
                {
                    field: 'duplication_number',
                    title: 'Duplications',
                    sortable: true,
                },
            ],
            data: [],
            detailView: true,
            detailFormatter: duplication_detail_formatter,
            detailViewIcon: true,
            detailViewByClick: false,
        });
        return;
    }

    // we need to extract the number duplications and format it
    const values = Object.values(duplicated_code_analysis["duplications"]);
    let duplication_name_array = [];
    let index = 1;
    values.forEach((value) => {
        duplication_name_array.push({ duplication_number: `Duplication #${index}`, value: value });
        index++;
    });

    // Initialize the table with data
    $table.bootstrapTable({
        columns: [
            {
                field: 'duplication_number',
                title: 'Duplications',
                sortable: true,
            },
        ],
        data: duplication_name_array,
        detailView: true,
        detailFormatter: duplication_detail_formatter,
        detailViewIcon: true,
        detailViewByClick: false,
        showColumns: false,
        onPostBody: function() {
            // Force visibility of detail icons
            $table.find('.detail-icon').css({
                'color': '#495057',
                'font-weight': 'bold',
                'font-size': '1.2rem',
            });
            $table.find('.detail').css({
                'width': '5%',
            })
            $table.find('.detail-icon').parent().css({
                'text-align': 'center',
            });
        }
    });
}

function duplication_detail_formatter(index, row) {
    if (!row.value || row.value.length === 0) {
        return '<div class="p-3 text-muted">No function data available</div>'; //TODO: Vérifier qu'est-ce qui arrive lorsqu'il y a aucune duplication.
    }

    const analysis = row.value;
    let file_extension = "bash";
    let file_header = "";
    analysis._files.forEach((file) => {
        const { filename, columns, lines } = file;
        file_header += `
            <tr><td style="width: 100%">${filename} : from (ln ${lines.From}, col ${columns.From}) to (ln ${lines.To}, col ${columns.To})</td></tr>
        `;
        file_extension = filename.split(".")[1];
    });

    let fragment = analysis._fragment;
    fragment = fragment.replace(/\\n/g, '\n');
    const highlighted_fragment = hljs.highlight(
        fragment,
        { language: file_extension }
    ).value

    let html = `
        <div class="p-3">
            <table class="table table-sm table-striped">
                <tdbody>
                    ${file_header}
                    <tr>
                        <td>
                            <pre><code class="hljs">${highlighted_fragment}</code></pre>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;

    html += '</tbody></table></div>';
    return html;
}

function render_files_recommendations(duplicated_code_analysis) {
    // Initialize or refresh the table
    const $table = $('#recommendations-table');
    
    // Destroy existing table if it exists
    if ($table.bootstrapTable('getOptions')) {
        $table.bootstrapTable('destroy');
    }

    // Check if duplicated_code_analysis exists and has recommendations
    if (!duplicated_code_analysis || !duplicated_code_analysis["recommendations"]) {
        // Initialize empty table if no data
        $table.bootstrapTable({
            columns: [
                {
                    field: 'filename',
                    title: 'Problems and recommendations',
                    sortable: true,
                },
            ],
            data: [],
            detailView: true,
        });
        return;
    }

    let recommendations_array = [];
    if (duplicated_code_analysis["recommendations"]["_global"]) {
        recommendations_array.push({ filename: "Global", value: duplicated_code_analysis["recommendations"]["_global"] });
    }
    
    if (duplicated_code_analysis["recommendations"]["_files"]) {
        const values = Object.values(duplicated_code_analysis["recommendations"]["_files"]);
        values.forEach((value) => {
            if (value.problems && value.problems.length > 0) {
                recommendations_array.push({ filename: value.subject, value: value});
            }
        });
    }

    // Initialize the table with data
    $table.bootstrapTable({
        columns: [
            {
                field: 'filename',
                title: 'Problems and recommendations',
                sortable: false,
            },
        ],
        data: recommendations_array,
        detailView: true,
        detailFormatter: recommendations_detail_formatter,
        detailViewIcon: true,
        detailViewByClick: false,
        showColumns: false,
        onPostBody: function() {
            // Force visibility of detail icons
            $table.find('.detail-icon').css({
                'color': '#495057',
                'font-weight': 'bold',
                'font-size': '1.2rem',
            });
            $table.find('.detail').css({
                'width': '5%',
            })
            $table.find('.detail-icon').parent().css({
                'text-align': 'center',
            });
        }
    });
}

function recommendations_detail_formatter(index, row) {
    if (!row.value.problems || row.value.problems.length === 0) {
        return '<div class="p-3 text-muted">No recommendation data available</div>';
    }

    const analysis = row.value;

    //let problems_list = '<td style="width: 100%">';
    let problem_count = 0;
    let problems_list = "<ul>";
    analysis.problems.forEach((problem) => {
        //problems_list += `${problem_count}. ${problem} <br />`;
        problem_count++;
        problems_list += `<li> ${problem} </li>`;
    });
    problems_list += "</ul>";
    const problems_text = (problem_count > 1) ? "Problems" : "Problem";
    //problems_list += '</td>'

    let recommendations_list = "<ul>";
    let recommendations_count = 0;
    analysis.recommendations.forEach((recommendation) => {
        //recommendations_list += `<td style="width: 100%">${recommendations_count}. ${recommendation}</td>`;
        recommendations_count++;
        recommendations_list += `<li> ${recommendation} </li>`;
    });
    recommendations_list += `</ul>`
    const recommendations_text = (recommendations_count > 1) ? "Recommendations" : "Recommendation";


    let html = `
        <div class="p-3">
            <table class="table table-sm table-striped">
                <tbody>
                    <tr>
                        <td class="d-flex align-center">&nbsp;${problems_text}</td>
                        <td class="d-flex align-center" style="width: 100%" >${problems_list}</td>
                    </tr>
                    <tr>
                        <td class="d-flex align-center">&nbsp;${recommendations_text}</td>
                        <td class="d-flex align-center" width: 100%>${recommendations_list}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;

    html += '</tbody></table></div>';
    return html;
}


function createNewFileMapSet(fileMap, fileName) {
    if (!fileMap.has(fileName)) {
        fileMap.set(fileName, {
            fileName: fileName,
            functions: [],
            avgComplexity: null,
            identifiableIdentitiesCount: 0,
            duplicateCodeCount: 0,
            priorityScore: 0
        });
    }
}

function export_to_json() {
    const data = {
        "metrics": to_export_metrics,
        "global_stats": to_export_global_stats,
        "commit": {
            "sha": commit_sha_display.textContent,
            "date": commit_date_display.textContent,
            "message": commit_message_display.textContent
        }
    };

    // https://javascript.plainenglish.io/javascript-create-file-c36f8bccb3be
    const content = JSON.stringify(data);
    const file = new File([content], "analysis.json", {type: "text/json"});
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.remove(link);
    window.URL.revokeObjectURL(url);
    window.location.reload()
}

