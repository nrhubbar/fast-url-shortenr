const origin = window.location.origin;

document.getElementById("submit-shorten").addEventListener("click", async () => {


    const data = {
        url: document.getElementById("url-input").value,
    };

    fetch(`${origin}/`, {
        method: "POST",
        mode: "same-origin",
        headers: {
            'Content-Type': "application/json",
        },
        body: JSON.stringify(data),
    }).then((response) => { 
        console.dir(response);
        return response.json();
    }).then((data) => {
            document.getElementById("short-url-container").innerHTML = `
                <p> Your Short URL is: <pre>${origin}/${data.shortUrl}</pre> </p>
            `;
        });
})