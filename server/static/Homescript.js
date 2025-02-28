const images = [
    'https://cdn.pixabay.com/photo/2012/12/24/08/39/disabled-72211_1280.jpg',
    'https://cdn.pixabay.com/photo/2021/05/30/19/11/wheelchair-6296811_1280.jpg',
    'https://cdn.pixabay.com/photo/2017/09/02/10/53/football-2706939_1280.jpg',
    'https://cdn.pixabay.com/photo/2016/07/17/14/27/hamburg-1523854_1280.jpg'
];

let currentIndex = 0;
const imageContainer = document.querySelector('.image-container');

function changeBackgroundImage() {
    currentIndex = (currentIndex + 1) % images.length;
    imageContainer.style.backgroundImage = `url('${images[currentIndex]}')`;
}

setInterval(changeBackgroundImage, 5000);