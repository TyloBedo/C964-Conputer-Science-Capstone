

let current_step:number = 1;

function go_to_step(step:number) {
    const steps:number[] = [1,2,3];
    for (let i:number = 0; i < steps.length; i++) {
        const step_elements: NodeListOf<HTMLElement> = document.querySelectorAll(`.step${steps[i]}`)
        step_elements.forEach((element:HTMLElement) => {
            if (step == steps[i]) {
                element.style.display = "block";
            }
            else {
                element.style.display = "none"
            }
        })
    }
}

function load_image(data:any) {
    const image_div = document.getElementById("image-location");
    const image = document.createElement("img");
    image.src = data;
    image.alt = "Plot image";
    image.id = "plot-image";

    image_div.appendChild(image);
}

function get_graph() {
        const data_area = document.getElementById("data-area") as HTMLTextAreaElement;
        const data = {"data": data_area.value}
        fetch('/submit-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(resp => resp.json())
        .then(data => {
            load_image(data['data'])
            go_to_step(2)
        })
        .catch(error => {console.error(error);
        });
}


function add_listeners() {
    const data_area = document.getElementById("data-area") as HTMLTextAreaElement;

    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
            data_area.value = content;
        } else {
            console.error("File content is not a string.");
        }
    };

    const data_set_buttons: NodeListOf<Element> = document.querySelectorAll(".load-data-set");
    data_set_buttons.forEach((element: Element) => {
        element.addEventListener("click", (e: Event) => {
            const target = e.target as HTMLElement;
            fetch(`/load-data/${target.id}`)
                .then(res => res.json())
                .then((data) => {
                    data_area.value = data['data'];
                })
        })
    })

    const file_upload = document.getElementById("file") as HTMLInputElement;
    file_upload.addEventListener("change", (event: Event) => {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) {
            console.error("No file selected");
            return;
        }
        reader.readAsText(input.files[0]);
    })


    const submit_button = document.getElementById("submit-data") as HTMLButtonElement;
    submit_button.addEventListener("click", get_graph)

    const step3_button = document.getElementById("gotostep3") as HTMLButtonElement;
    step3_button.addEventListener("click", () => {
      go_to_step(3)
    })

}

document.addEventListener("DOMContentLoaded", () => {
  add_listeners()
})