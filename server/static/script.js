var info = true;

const portatilEl = document.querySelector('.portatil');
const reproductorEl = document.querySelector('.reproductor');
const expoEl = document.querySelector('.expo');
const infoEl = document.querySelector('.info');
const infoImgEl = document.querySelector('.info img');

// Definimos el media query
const screenQuery = window.matchMedia('(max-width: 900px)');

// Función para actualizar el ancho según el tamaño de pantalla
function updateReproductorWidth(e) {
  if (e.matches) {
    reproductorEl.style.width = '100%';
  }
}

// Escuchamos el cambio en el media query
screenQuery.addEventListener('change', updateReproductorWidth);
updateReproductorWidth(screenQuery);

// Listener para el clic en .info, solo en pantallas grandes
infoEl.addEventListener('click', function() {
  if (!screenQuery.matches) {
    if (info) {
      reproductorEl.style.width = '40%';
      infoImgEl.src = 'https://cdn-icons-png.flaticon.com/512/660/660350.png';
      expoEl.style.display = 'flex';
    } else {
      reproductorEl.style.width = '80%';
      infoImgEl.src = 'https://cdn-icons-png.flaticon.com/512/2258/2258853.png';
      expoEl.style.display = 'none';
    }
    info = !info;
  }
});

// Animación secuencial de imágenes en .persona
document.addEventListener("DOMContentLoaded", function () {
  const items = document.querySelectorAll(".persona ul li");

  if (items.length === 0) {
    console.error("No se encontraron elementos <li> en .persona");
    return;
  }

  function animarImagen(item, callback) {
    const imagen = item.querySelector("img");

    if (!imagen) {
      console.error("No se encontró una imagen en", item);
      callback();
      return;
    }

    function iniciarAnimacion() {
      const alturaImagen = imagen.clientHeight;
      console.log("Altura de la imagen:", alturaImagen);
      const desplazamiento = 150;
      let maxMovimientos = Math.floor(alturaImagen / desplazamiento);
      maxMovimientos = maxMovimientos > 0 ? maxMovimientos - 1 : 0;

      let posicion = 0;
      let movimientos = 0;

      const intervalo = setInterval(() => {
        if (movimientos < maxMovimientos) {
          posicion -= desplazamiento;
          imagen.style.marginTop = `${posicion}px`;
          movimientos++;
        } else {
          clearInterval(intervalo);
          callback();
        }
      }, 70);
    }

    if (imagen.complete) {
      iniciarAnimacion();
    } else {
      imagen.onload = iniciarAnimacion;
    }
  }

  function animarSecuencial(index) {
    if (index < items.length) {
      animarImagen(items[index], () => {
        animarSecuencial(index + 1);
      });
    } else {
      console.log("Todas las imágenes han sido animadas");
    }
  }

  animarSecuencial(0);
});

// Variable para evitar llamadas múltiples a agregarNuevoVideo
let isFetchingNewVideo = false;

// Función para iniciar el Intersection Observer en videos
function iniciarObservadorVideos() {
  const observer = new IntersectionObserver((entries) => {
    let maxRatio = 0;
    let activeEntry = null;
    
    entries.forEach(entry => {
      if (entry.isIntersecting && entry.intersectionRatio > maxRatio) {
        maxRatio = entry.intersectionRatio;
        activeEntry = entry;
      }
    });
    
    const cuadros = document.querySelectorAll('.cuadro');
    if (activeEntry) {
      const video = activeEntry.target;
      const videoList = Array.from(document.querySelectorAll('.video_player'));
      const index = videoList.indexOf(video);
      
      let activeAnnIndex = (index === 1) ? 1 : 0;
      
      cuadros.forEach((cuadro, i) => {
        cuadro.style.display = (i === activeAnnIndex) ? "flex" : "none";
      });
      
      video.play();
      
      if (videoList.indexOf(video) === videoList.length - 1 && !isFetchingNewVideo) {
        isFetchingNewVideo = true;
        agregarNuevoVideo().finally(() => {
          isFetchingNewVideo = false;
        });
      }
    } else {
      cuadros.forEach(cuadro => {
        cuadro.style.display = "none";
      });
    }
    
    if (Array.from(cuadros).every(cuadro => cuadro.style.display === "none")) {
      cuadros[1].style.display = "flex";
    }
    
    entries.forEach(entry => {
      if (!entry.isIntersecting) {
        entry.target.pause();
        entry.target.currentTime = 0;
      }
    });
  }, { threshold: 0.5 });
  
  document.querySelectorAll('.video_player').forEach(video => observer.observe(video));
  return observer;
}

let observer;
document.addEventListener("DOMContentLoaded", () => {
  observer = iniciarObservadorVideos();
});

function agregarNuevoVideo() {
  return fetch("/nuevo_video")
    .then(response => response.json())
    .then(data => {
      if (data.video_url) {
        const videosContainer = document.querySelector(".videos");
        const videos = document.querySelectorAll(".player");

        if (videos.length >= 3) {
          videos[0].remove();
        }

        const nuevoDiv = document.createElement("div");
        nuevoDiv.classList.add("player");
        const nuevoVideo = document.createElement("video");
        nuevoVideo.src = data.video_url;
        nuevoVideo.classList.add("video_player");
        nuevoVideo.autoplay = true;
        nuevoVideo.loop = true;

        nuevoDiv.appendChild(nuevoVideo);
        videosContainer.appendChild(nuevoDiv);

        observer.observe(nuevoVideo);
      }
    })
    .catch(error => console.error("Error obteniendo nuevo video:", error));
}


document.addEventListener("DOMContentLoaded", function () {
  function eliminarImagenes() {
    document.querySelectorAll("li img").forEach(img => {
      const marginTop = parseInt(window.getComputedStyle(img).marginTop);
      if (marginTop === -1650) {
        img.remove();
        console.log("Imagen eliminada:", img);
      }
    });
  }

  // Observador de mutaciones para detectar cambios en la lista <ul>
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.type === "childList") {
        eliminarImagenes(); // Aplicar eliminación cuando se agregue un nuevo <li>
      }
    });
  });

  // Selecciona la lista <ul> donde se agregan los <li>
  const targetNode = document.querySelector(".persona ul");
  if (targetNode) {
    observer.observe(targetNode, { childList: true });
  }

  // También ejecutamos la función al inicio
  eliminarImagenes();

  // Ejecutar periódicamente por si hay cambios sin mutaciones detectadas
  setInterval(eliminarImagenes, 1000);
});
