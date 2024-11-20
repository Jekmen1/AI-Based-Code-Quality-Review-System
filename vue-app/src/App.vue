<template>
  <div>
    <h1>welcome to homepage</h1>
    <h2>you can start using AI here</h2>
    <button id="button">drag here</button>
  </div>
</template>
<script setup lang="ts"></script>

<style>
div {
  text-align: center;
  position: relative;
  top: 235px;
}

h1 {
  font-family: Arial;
  text-transform: uppercase;
  color: aliceblue;
}

h2 {
  font-family: Arial;
  text-transform: uppercase;
  color: aliceblue;
}

button {
  width: 150px;
  height: 50px;
  border: green solid 2px;
  border-radius: 3cap;
  background-color: lawngreen;
  font-family: Arial;
  font-size: medium;
}

button:hover {
  transform: scale(1.1);
  transition: ease 0.3s;
  background-color: cyan;
  border: deepskyblue;
}

button:active {
  transform: scale(1.1);
  transition: ease 0.3s;
  background-color: blueviolet;
  border: purple;
}

body {
  background-image: url("https://wallpaperboat.com/wp-content/uploads/2019/10/coding-12.jpg");
}
</style>
