var page_data = { 'job_data': "", 'teams': 8, 'employees': 26, 'step': 1 };
document.addEventListener("DOMContentLoaded", function () {
    add_listeners();
});
function next_step() {
    if (!page_data['job_data'].includes("location,budget,latitude,longitude")) {
        alert("Location data invald! Make sure your data contains the headers: \n" +
            "location,budget,latitude,longitude");
        return;
    }
    if (page_data['job_data'].trim().split("\n").length < 3) {
        alert("Location data invald! You need to enter at least two locations \n" +
            "the first of which is your home location");
        return;
    }
    var next_step = eval("step".concat(page_data['step'] + 1));
    send_data(next_step);
    page_data['step'] = page_data['step'] + 1;
    go_to_step(page_data['step']);
}
function go_to_step(step) {
    var step_elements = document.querySelectorAll("[class*='step']");
    console.log(step_elements);
    step_elements.forEach(function (element) {
        if (element.classList.contains("step".concat(step)))
            element.style.display = "block";
        else
            element.style.display = "none";
    });
}
function load_image(data, target) {
    var image_div = document.getElementById("".concat(target));
    var image = document.createElement("img");
    image.src = data;
    image.alt = "Plot image";
    image_div.innerHTML = "";
    image_div.appendChild(image);
}
function step2(data) {
    load_image(data['data'], "job-plot");
    document.getElementById("emp-count").innerHTML = data['min_employees'];
    document.getElementById("team-count").innerHTML = data['min_teams'];
    var employees = document.getElementById("employees");
    employees.min = data['min_employees'];
    var teams = document.getElementById("teams");
    teams.min = data['min_teams'];
}
function step3(data) {
    //Setup step 3
    load_image(data['data'], "team-plot");
    load_image(data['labor_plot'], "labor-plot");
    document.getElementById("route-table").innerHTML = data['table'];
}
function send_data(callback) {
    fetch("/submit-data", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(page_data),
    })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
        callback(data);
    })
        .catch(function (error) {
        console.error(error);
    });
}
function update_job_data(data) {
    var data_area = document.getElementById("data-area");
    data_area.value = data;
    page_data['job_data'] = data;
}
function add_listeners() {
    var data_area = document.getElementById("data-area");
    data_area.addEventListener("change", function () {
        page_data['job_data'] = data_area.value;
    });
    var reader = new FileReader();
    reader.onload = function (event) {
        var _a;
        var content = (_a = event.target) === null || _a === void 0 ? void 0 : _a.result;
        if (typeof content === 'string') {
            update_job_data(content);
        }
        else {
            console.error("File content is not a string.");
        }
    };
    var data_set_buttons = document.querySelectorAll(".load-data-set");
    data_set_buttons.forEach(function (element) {
        element.addEventListener("click", function (e) {
            var target = e.target;
            fetch("/load-data/".concat(target.id))
                .then(function (res) { return res.json(); })
                .then(function (data) {
                update_job_data(data['data']);
            });
        });
    });
    var file_upload = document.getElementById("file");
    file_upload.addEventListener("change", function (event) {
        var input = event.target;
        if (!input.files || input.files.length === 0) {
            console.error("No file selected");
            return;
        }
        reader.readAsText(input.files[0]);
    });
    var employees = document.getElementById("employees");
    employees.addEventListener("change", function () {
        if (employees.valueAsNumber < parseInt(employees.min)) {
            employees.value = employees.min;
            alert("Minimum value for employees must be ".concat(employees.min));
        }
        page_data['employees'] = employees.valueAsNumber;
    });
    var teams = document.getElementById("teams");
    teams.addEventListener("change", function () {
        if (teams.valueAsNumber < parseInt(teams.min)) {
            teams.value = teams.min;
            alert("Minimum value for teams must be ".concat(teams.min));
        }
        page_data['teams'] = teams.valueAsNumber;
    });
    document.querySelectorAll(".next").forEach(function (element) {
        element.addEventListener("click", next_step);
    });
}
