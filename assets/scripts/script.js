String.prototype.replaceChars = function(character, replacement) {
    var str = this;
    var a;
    var b;
    for(var i=0; i < str.length; i++) {
        if(str.charAt(i) == character) {
            a = str.substr(0, i) + replacement;
            b = str.substr(i + 1);
            str = a + b;
        }
    }
    return str;
}

Number.prototype.normalize = function() {
    if (this.valueOf() < 10) {
        return "0"+this.valueOf();
    }
    return "" +this.valueOf();
}

/*
 *
 *
 */
function updateClock() {
    var date = new Date();
    document.getElementById("time").innerHTML = date.getHours().normalize() + ":" + date.getMinutes().normalize() + ":" + date.getSeconds().normalize();
}

/*
 *
 *
 */
function updateDate() {
    var date = new Date();
    document.getElementById("date").innerHTML = date.getDate().normalize() + "." + (date.getMonth()+1).normalize() + "." + date.getFullYear();
}

/*
 *
 *
 */
function hideable_value_restore() {
    document.getElementById("display_hideable_cards").checked = (localStorage.getItem("display_hideable_cards") == 'true');
}

/*
 *
 *
 */
function hideable_value_store() {
    localStorage.setItem("display_hideable_cards", document.getElementById("display_hideable_cards").checked);
    this.set_card_visibliy();
}

/*
 *
 *
 */
function set_card_visibliy() {
    var work_divs = document.getElementsByClassName("hideable");

    for (let index = 0; index < work_divs.length; index++) {
        const element = work_divs[index];
        // If the checkbox is checked, display the output text
        if (localStorage.getItem("display_hideable_cards") == 'true'){
            element.style.display = "block";
        } else {
            element.style.display = "none";
        }
    }
}

/*
 *
 *
 */
function search(query){
    switch(query.substr(0, 2)){
        case "-d":
            query = query.substr(3);
            window.location = "https://duckduckgo.com/?q=" +
            query.replaceChars(" ", "+");
            break;
        
        case "-g":
            query = query.substr(3);
            window.location="https://www.google.at/search?q=" +
            query.replaceChars("", "+");
            break;

        case "-r":
            query = query.substr(3);
            window.location = "https://www.reddit.com/search?q=" +
            query.replaceChars(" ", "+");
            break;

        case "-y":
            query = query.substr(3);
            window.location =
            "https://www.youtube.com/results?search_query=" +
            query.replaceChars(" ", "+");
            break;
        default:
            window.location="https://www.startpage.com/do/dsearch?prfe=36c84513558a2d34bf0d89ea505333ad59fcc4f8848a538a0c1c89932309a9bc5065027ac0acf304745625d261b6aec0&query=" +
            query.replaceChars("", "+");
    }
}

window.onload = function() {
    // date and time
    this.updateClock();
    this.updateDate();
    this.setInterval(updateClock, 1000);

    // hideable cards
    if (localStorage.getItem("display_hideable_cards")) {
        this.hideable_value_restore();
        this.set_card_visibliy();
    } else {
        this.hideable_value_store();
    }

    // search-bar
    searchinput = document.getElementById("search-bar");
    if(!!searchinput){
        searchinput.addEventListener("keypress", function(a){
            var key = a.keyCode;
            if(key == 13){
                var query = this.value;
                search(query);
            }
        });
    }
    // jump to search when tab is pressed
    var search_sqr = document.getElementById("search-bar");
}