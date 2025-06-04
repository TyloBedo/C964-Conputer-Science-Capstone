let page_data:{} = {'job_data':"", 'teams':8, 'employees':26, 'step':1}

document.addEventListener("DOMContentLoaded", ():void => {
  add_listeners()
})

function next_step():void {
    if(!page_data['job_data'].includes("location,budget,latitude,longitude")){
        alert("Location data invald! Make sure your data contains the headers: \n" +
              "location,budget,latitude,longitude")
        return
    }
    if(page_data['job_data'].trim().split("\n").length < 3){
        alert("Location data invald! You need to enter at least two locations \n" +
            "the first of which is your home location")
        return

    }
    const next_step:() => void = eval(`step${page_data['step'] + 1}`)
    send_data(next_step)
    page_data['step'] = page_data['step'] + 1;
    go_to_step(page_data['step']);
}

function go_to_step(step:number):void {
    const step_elements: NodeListOf<HTMLElement> = document.querySelectorAll("[class*='step']" )
    console.log(step_elements)
    step_elements.forEach((element:HTMLElement):void => {
        if (element.classList.contains(`step${step}`))
            element.style.display = "block";
        else
            element.style.display = "none"
    })
}

function load_image(data:string, target:string):void {
    const image_div:HTMLElement = document.getElementById(`${target}`);
    const image:HTMLImageElement = document.createElement("img");
    image.src = data;
    image.alt = "Plot image";
    image_div.innerHTML = "";
    image_div.appendChild(image);
}

function step2(data:{}):void {
    load_image(data['data'], "job-plot");
    document.getElementById("emp-count").innerHTML = data['min_employees'];
    document.getElementById("team-count").innerHTML = data['min_teams'];
    const employees = document.getElementById("employees") as HTMLInputElement;
    employees.min  = data['min_employees'];
    const teams = document.getElementById("teams") as HTMLInputElement;
    teams.min = data['min_teams'];
}

function step3(data:{}):void {
    //Setup step 3
    load_image(data['data'], "team-plot")
    load_image(data['labor_plot'], "labor-plot")
    document.getElementById("route-table").innerHTML = data['table'];
}
function send_data(callback: (arg0:{} ) => void ) {
    fetch("/submit-data", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(page_data),
    })
    .then(resp => resp.json())
    .then(data => {
        callback(data)
    })
    .catch(error => {console.error(error);
    });
}

function update_job_data(data:string):void {
    const data_area = document.getElementById("data-area") as HTMLTextAreaElement;
    data_area.value = data;
    page_data['job_data'] = data;
}

function add_listeners():void {

  const data_area = document.getElementById("data-area") as HTMLTextAreaElement;
  data_area.addEventListener("change", ():void => {
    page_data['job_data'] = data_area.value;
  })

  const reader = new FileReader();
  reader.onload = (event:ProgressEvent<FileReader>):void => {
    const content:string|ArrayBuffer = event.target?.result;
    if (typeof content === 'string') {
        update_job_data(content)
    } else {
        console.error("File content is not a string.");
    }
  };

  const data_set_buttons: NodeListOf<Element> = document.querySelectorAll(".load-data-set");
  data_set_buttons.forEach((element: Element):void => {
    element.addEventListener("click", (e: Event):void => {
      const target = e.target as HTMLElement;
      fetch(`/load-data/${target.id}`)
        .then(res => res.json())
        .then((data:{}):void => {
            update_job_data(data['data'])
        })
      })
  });

  const file_upload = document.getElementById("file") as HTMLInputElement;
  file_upload.addEventListener("change", (event: Event):void => {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
        console.error("No file selected");
        return;
    }
    reader.readAsText(input.files[0]);
  });

  const employees = document.getElementById("employees") as HTMLInputElement;
  employees.addEventListener("change", ():void => {
    if(employees.valueAsNumber < parseInt(employees.min)){
        employees.value = employees.min;
        alert(`Minimum value for employees must be ${employees.min}`)
    }
    page_data['employees'] = employees.valueAsNumber;
  });

  const teams = document.getElementById("teams") as HTMLInputElement;
  teams.addEventListener("change", ():void => {
    if(teams.valueAsNumber < parseInt(teams.min)){
        teams.value = teams.min;
        alert(`Minimum value for teams must be ${teams.min}`)
    }
    page_data['teams'] = teams.valueAsNumber;
  });

  document.querySelectorAll(".next").forEach((element:Element):void => {
    element.addEventListener("click", next_step);
  })
}

