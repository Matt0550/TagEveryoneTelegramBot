function errorAlert(message) {
    window.Telegram.WebApp.HapticFeedback.notificationOccurred("error");
    window.Telegram.WebApp.showAlert("Error: " + message);
}

function leaveGroup(group_id) {
    // Confirm
    window.Telegram.WebApp.showConfirm("Are you sure you want to leave this list? You can rejoin at any timi with /in command.", function (result) {
        if (result) {
            
            fetch("/leaveInListGroup", {
                method: "POST",
                body: JSON.stringify({
                    "init_data": TG_INIT_DATA,
                    "hash": TG_INIT_HASH,
                    "group_id": group_id
                }),
                headers: {
                    "Content-Type": "application/json"
                }
            }).then(function (response) {
                return response.json();
            }).then(function (data) {
                if (data.status !== 200) {
                    if (data.status === 401) {
                        $("#unauthorized").show();
                    }
                    console.log("Error", data.message);
                    errorAlert(data.message);

                    return;
                }
                window.Telegram.WebApp.HapticFeedback.notificationOccurred("success");
                window.Telegram.WebApp.showAlert("Success: " + data.message);
                window.location.reload();
            });
        }
    });
}


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
        console.log(data);

        if (data.status !== 200) {
            if (data.status === 401) {
                $("#unauthorized").show();
            }
            console.log("Error", data.message);
            errorAlert(data.message);

            return;
        }
        if (data.isOwner) {
            window.Telegram.WebApp.MainButton.text = "Admin Panel";
            window.Telegram.WebApp.MainButton.show();

            window.Telegram.WebApp.MainButton.onClick(function () {
                window.Telegram.WebApp.MainButton.showProgress();
                fetch("/getAdminPanel", {
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
                    console.log(data);
                    window.Telegram.WebApp.MainButton.hideProgress();

                    if (data.status !== 200) {
                        if (data.status === 401) {
                            $("#unauthorized").show();
                        }
                        console.log("Error", data.message);
                        errorAlert(data.message);

                        return;
                    }

                    $("#group-div").hide();
                    window.Telegram.WebApp.MainButton.hide();
                    window.Telegram.WebApp.BackButton.onClick(function () {
                        window.Telegram.WebApp.BackButton.hide();
                        window.Telegram.WebApp.MainButton.show();
                        $("#group-div").show();
                        $("#log-div").hide();
                    });
                    window.Telegram.WebApp.BackButton.show();

                    $("#log-list").empty();

                    const logs = data.logs;
                    $("#log-count").text(logs.length);

                    if (logs.length === 0) {
                        $("#log-list").append(`
                        <div class="flex flex-row justify-between items-center bg-gray-200 rounded-lg p-4 mb-2">
                                <div class="flex flex-col">
                                    <h1 class="text-lg font-bold text-gray-700">No logs</h1>
                                    <p class="text-sm text-gray-500">No logs found.</p>
                                </div>
                            </div>
                        `);
                    }

                    for (let i = 0; i < logs.length; i++) {
                        const log = logs[i];
                        $("#log-list").append(`
                        <div class="flex flex-row justify-between items-center rounded-lg p-4 mb-2" style="background-color: var(--tg-theme-secondary-bg-color);">
                                <div class="flex flex-col">
                                    <h1 class="text-lg font-bold">${log.action}</h1>
                                    <p class="text-sm" style="color: var(--tg-theme-hint-color);">${log.description}</p>
                                    <p class="text-sm" style="color: var(--tg-theme-hint-color);">${log.datetime}</p>
                                    <p class="text-sm" style="color: var(--tg-theme-hint-color);">User ID: ${log.user_id}</p>
                                    <p class="text-sm" style="color: var(--tg-theme-hint-color);">Chat ID: ${log.group_id}</p>
                                </div>
                            </div>
                        `);
                    }

                });
                $("#log-div").show();

                window.Telegram.WebApp.BackButton.show();

            });

        }

        const groups = data.groups;

        if (groups.length === 0) {
            $("#group-list").append(`
            <div class="flex flex-row justify-between items-center bg-gray-200 rounded-lg p-4 mb-2">
                    <div class="flex flex-col">
                        <h1 class="text-lg font-bold text-gray-700">No groups</h1>
                        <p class="text-sm text-gray-500">You are not included in any tag list. To join a group, use the <b>/in</b> command.</p>
                    </div>
                </div>
            `);
        }

        for (let i = 0; i < groups.length; i++) {
            const group = groups[i];
            $("#group-list").append(`
            <div class="flex flex-row justify-between items-center rounded-lg p-4 mb-2" style="background-color: var(--tg-theme-secondary-bg-color);">
                    <div class="flex flex-col">
                        <h1 class="text-lg font-bold">${group.name}</h1>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">${group.members} members</p>
                    </div>
                    <div class="flex flex-row">
                        <button class="text-white font-bold py-2 px-4 rounded" style="background-color: var(--tg-theme-button-color)" onclick="leaveGroup(${group.group_id})">
                            Leave list
                        </button>
                    </div>
                </div>
            `);
        }
    });

    window.Telegram.WebApp.ready();

});

const TG_INIT_DATA = window.Telegram.WebApp.initData;
// Convert key=val  to {key: val}
const TG_INIT_DATA_DICT = TG_INIT_DATA.split("&").reduce((acc, curr) => {
    const [key, val] = curr.split("=");
    acc[key] = val;
    return acc;
}, {});

const TG_INIT_HASH = TG_INIT_DATA_DICT.hash;