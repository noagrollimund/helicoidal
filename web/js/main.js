async function buildImagePage(image_path) {
  console.log(image_path)
  let body = document.getElementById("body")
  body.innerHTML = `    <div class="outsideWrapper">
  <div class="insideWrapper">
      <img id="image" class="coveredImage">
      <canvas id="canvas" class="coveringCanvas"></canvas>
  </div>

  <div id = "radio-container">
      <input type="radio" id="add-ruler-point" name="mode" value="add_ruler_point">
      <label for="add-ruler-point">Add ruler point</label><br>
      <input type="radio" id="delete-ruler-point" name="mode" value="delete_ruler_point">
      <label for="delete-ruler-point">Delete ruler point</label><br>
      <input type="radio" id="move-tube-side" name="mode" value="move_tube_side">
      <label for="move-tube-side">Move tube side</label><br>
      <input type="radio" id="add-water" name="mode" value="add_water">
      <label for="add-water">Add water</label><br>
      <input type="radio" id="delete-water" name="mode" value="delete_water">
      <label for="delete-water">Delete water</label><br>  
  </div>
  <div id = "radio-valid-container-2">
      <div id="ruler-value-container">
          <label for="ruler-value">Ruler value :</label><br>
          <input type="text" id="ruler-value" name="ruler-value" value="1"><br>
      </div>
      <input type="radio" id="is-not-valid" name="valid-or-not" value="false">
      <label for="is-not-valid">Not validated</label>
      <input type="radio" id="is-valid" name="valid-or-not" value="true">
      <label for="is-valid">Validated</label>
  </div>`


  let canvas = document.getElementById("canvas");
  let img = document.getElementById("image");
  img.setAttribute("src",image_path);


  function getPercentageMousePos(canvas, event) {
      var rect = canvas.getBoundingClientRect();
      return {
        x: (event.clientX - rect.left) / rect.width,
        y: (event.clientY - rect.top) / rect.height
      }
  }

  function getMode() {
    let radios = document.getElementsByName('mode');

    for (var i = 0, length = radios.length; i < length; i++) {
      if (radios[i].checked) {
        return radios[i].value   
    }
  }
  }

  canvas.addEventListener('click', function(event) {
      let pos = getPercentageMousePos(canvas, event);
      let image_path = img.getAttribute("src")
      let mode = getMode()
      eel.deal_with_click(pos.x, pos.y, mode, image_path);
      img.setAttribute("src",image_path);
  });

  // deal with the validity of the image
  let radios = document.getElementsByName('valid-or-not');
  let initialValidity = await eel.get_image_validity(image_path)();
  if (initialValidity == "true") {
    document.getElementById("is-valid").checked = true;
    document.getElementById("is-not-valid").checked = false;
  } else {
    document.getElementById("is-valid").checked = false;
    document.getElementById("is-not-valid").checked = true;
  }
  let prev = null;
  for (var i = 0; i < radios.length; i++) {
      radios[i].addEventListener('change', function() {
          if (this !== prev) {
              prev = this;
              eel.change_image_validity(img.getAttribute("src"), this.value)
          }
      });
  }

  // set ruler value
  let rulerValue = document.getElementById('ruler-value');
  let initialRulerValue = await eel.get_ruler_value(image_path)();
  rulerValue.setAttribute("value", initialRulerValue);
  rulerValue.addEventListener('change', function() {
    eel.change_ruler_value(img.getAttribute("src"), this.value);
  });
}

async function buildHomePage() {
  let body = document.getElementById("body");
  body.innerHTML = `
  <div id = "radio-valid-container">
    <input type="radio" id="is-not-valid" name="valid-or-not" value="false" checked>
    <label for="is-not-valid">Not validated</label>
    <input type="radio" id="is-valid" name="valid-or-not" value="true">
    <label for="is-valid">Validated</label>
  </div>
<div id = "image-container"></div>`;
  buildImageMosaic("false");

  let radios = document.getElementsByName('valid-or-not');
  let prev = null;
  for (var i = 0; i < radios.length; i++) {
      radios[i].addEventListener('change', function() {
          if (this !== prev) {
              prev = this;
              buildImageMosaic(this.value)
          }
      });
  }
}
  



async function buildImageMosaic (valid) {
  function buildImagePageDelegate(image_path) {
    return function(){
        buildImagePage(image_path)
    }
  }

  let listFiles = await eel.get_list_image_path(valid)();
  let imageContainer = document.getElementById("image-container");
  imageContainer.innerHTML = ""
  for (let i in listFiles) {
      file = listFiles[i]
      let image = document.createElement("img");
      image.classList.add("small-image");
      image.setAttribute("src", file);
      image.addEventListener('click', buildImagePageDelegate(file))
      imageContainer.appendChild(image);
  }
}


buildHomePage()


