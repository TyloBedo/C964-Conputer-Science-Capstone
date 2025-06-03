let current_step:number = 1;
let page_data:{} = {'job_data':"", 'teams':0, 'employees':0}


document.addEventListener("DOMContentLoaded", ():void => {
  add_listeners()
})


function go_to_step(step:number):void {

    const steps:number[] = [1,2,3];
    for (let i:number = 0; i < steps.length; i++) {
        const step_elements: NodeListOf<HTMLElement> = document.querySelectorAll(`.step${steps[i]}`)
        step_elements.forEach((element:HTMLElement):void => {
            if (step == steps[i]) {
                element.style.display = "block";
            }
            else {
                element.style.display = "none"
            }
        })
    }
}

function load_image(data:string, target:string):void {
    const image_div:HTMLElement = document.getElementById(`${target}`);
    const image:HTMLImageElement = document.createElement("img");
    image.src = data;
    image.alt = "Plot image";
    image_div.innerHTML = "";
    image_div.appendChild(image);
}



function step2():void {
    fetch('/submit-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(page_data),
    })
    .then(resp => resp.json())
    .then(data => {
        //setup step 2
        load_image(data['data'], "job-plot")
        go_to_step(2)
    })
    .catch(error => {console.error(error);
    });
}

function step3():void {
    fetch('/submit-final', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(page_data),
    })
    .then(resp => resp.json())
    .then(data => {

        //Setup step 3
        load_image(data['data'], "team-plot")
        document.getElementById("route-table").innerHTML = data['table'];
        go_to_step(3)



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
        page_data['employees'] = employees.valueAsNumber;
    });

    const teams = document.getElementById("teams") as HTMLInputElement;
    employees.addEventListener("change", ():void => {
        page_data['teams'] = teams.valueAsNumber;
    });


    const submit_button = document.getElementById("submit-data") as HTMLButtonElement;
    submit_button.addEventListener("click", step2);

    const step3_button = document.getElementById("gotostep3") as HTMLButtonElement;
    step3_button.addEventListener("click", step3);




}

