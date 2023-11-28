window.Telegram.WebApp.ready();
$(document).ready(function () {
    console.log("ready!");
    fetch("/getInGroups", {
        method: "POST",
        body: JSON.stringify({
            "init_data": TG_INIT_DATA,
            "hash": TG_INIT_HASH
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(function (response) {
        return response.json();
    }).then(function (data) {
        $("#loader").hide();
        console.log(data);

        if (data.status !== 200) {
            if (data.status === 401) {
                $("#unauthorized").show();
            }
            console.log("Error", data.message);
            window.Telegram.WebApp.HapticFeedback.notificationOccurred("error");
            window.Telegram.WebApp.showAlert("Error: " + data.message);

            return;
        }
        const groups = data.groups;

        for (let i = 0; i < groups.length; i++) {
            const group = groups[i];
            $("#group-list").append(`
            <div class="flex flex-row justify-between items-center bg-gray-200 rounded-lg p-4 mb-2">
                    <div class="flex flex-col">
                        <h1 class="text-lg font-bold text-gray-700">${group.name}</h1>
                        <p class="text-sm text-gray-500">${group.members} members</p>
                    </div>
                    <div class="flex flex-row">
                        <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                            Leave list
                        </button>
                    </div>
                </div>
            `);
        }
    });
});

const TG_INIT_DATA = window.Telegram.WebApp.initData;
// Convert key=val  to {key: val}
const TG_INIT_DATA_DICT = TG_INIT_DATA.split("&").reduce((acc, curr) => {
    const [key, val] = curr.split("=");
    acc[key] = val;
    return acc;
}, {});

const TG_INIT_HASH = TG_INIT_DATA_DICT.hash;