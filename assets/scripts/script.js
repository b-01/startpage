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

/* Update the current time  */
function updateClock() {
    var date = new Date();
    document.getElementById("time").innerHTML = date.getHours().normalize() + ":" + date.getMinutes().normalize() + ":" + date.getSeconds().normalize();
}

/* Update the date */
function updateDate() {
    var date = new Date();
    document.getElementById("date").innerHTML = date.getDate().normalize() + "." + (date.getMonth()+1).normalize() + "." + date.getFullYear();
}

/* Set or reset the checkbox value */ 
function hideable_value_restore() {
    document.getElementById("display_hideable_cards").checked = (localStorage.getItem("display_hideable_cards") == 'true');
}

/* Stores the checkbox status into localStorage and then updates card visiblity */
function hideable_value_store() {
    localStorage.setItem("display_hideable_cards", document.getElementById("display_hideable_cards").checked);
    this.set_card_visibliy();
}

/* Iterates through all "hideable" divs and either sets
 * them visible or hides them. */
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

/* Check if a string is a URL/Domain */
function is_url(str)
{
    regexp =  /^(?:(?:https?):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$/;
    if (regexp.test(str)) {
        return true;
    } else {
        return false;
    }
}

/* Search function. Either uses the keywords with the defined search engines, directly
 * opens the site in a new tab or uses the default search engine (startpage). 
 */
function search(query){
    switch(query.substr(0, 2)){
        // Duckduckgo - search with DDGO.
        case "-d":
            query = query.substr(3);
            window.location = "https://duckduckgo.com/?q=" +
            query.replaceChars(" ", "+");
            break;
        // DeepL - Translate Text from German to English
        case "-t":
            query = query.substr(3);
            window.location = "https://www.deepl.com/en/translator#de/en/" +
            encodeURIComponent(query)
            break;
        // Google - Google Search
        case "-g":
            query = query.substr(3);
            window.location="https://www.google.at/search?q=" +
            query.replaceChars("", "+");
            break;
        // Reddit - Reddit Search
        case "-r":
            query = query.substr(3);
            window.location = "https://www.reddit.com/search?q=" +
            query.replaceChars(" ", "+");
            break;
        // Youtube - Youtube Search
        case "-y":
            query = query.substr(3);
            window.location =
            "https://www.youtube.com/results?search_query=" +
            query.replaceChars(" ", "+");
            break;
        default:
            if (is_url(query)) {
                if (! query.startsWith("http")) {
                    query = "https://"+query;
                }
                window.location = query;
            } else {
                // use startpage as default search with dark mode enabled as default
                window.location="https://www.startpage.com/do/dsearch?prfe=36c84513558a2d34bf0d89ea505333ad59fcc4f8848a538a0c1c89932309a9bc5065027ac0acf304745625d261b6aec0&query=" +
                query.replaceChars("", "+");
            }
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