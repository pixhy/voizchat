<script setup lang="ts">

import { onMounted, onUnmounted, ref, inject } from 'vue';
import { useRoute } from 'vue-router';

const canvas = ref<HTMLCanvasElement | null>(null);
let drawing = false;
let prevX = 0, prevY = 0;
let ctx: CanvasRenderingContext2D | null = null;
let color = "black"
let lineWidth = 1;


const route = useRoute();
let channelId = Array.isArray(route.params.channelId) ? route.params.channel_id[0] : route.params.channelId;
const setWhiteBoardHandler = inject('setWhiteBoardHandler') as (handler: any) => {};
const sendWebsocketCommand = inject('sendWebsocketCommand') as (command: string, data: any) => {};

function onDraw(draw_data: DrawData){
  if(draw_data.channel_id !== channelId) {
    return false;
  }

  drawOnCanvas(draw_data.x, draw_data.y, draw_data.prevX, draw_data.prevY, draw_data.line_color, draw_data.line_width)
}

onMounted(() => {
  if (!canvas.value) return;
  canvas.value.style.width = canvas.value.width + 'px';
  canvas.value.style.height = canvas.value.height + 'px';
  ctx = canvas.value.getContext("2d");
  if (!ctx) return;
  ctx.fillStyle = "white"
  ctx.lineCap = "round";
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height);

  setWhiteBoardHandler(onDraw)
})
export interface DrawData {
  channel_id: string;
  x: number;
  y: number;
  prevX: number;
  prevY: number;
  line_width: number;
  line_color: string
}

onUnmounted(() => {
  setWhiteBoardHandler(null)
});


function startDrawing(e: MouseEvent){
    
  drawing = true;
  prevX = e.offsetX;
  prevY = e.offsetY;
  console.log("rajz")
}

function draw(e: MouseEvent){
    
  if (!drawing || !ctx) return;

  if(!(e.buttons & 1)){
    drawing = false;
    return;
  }

  const x = e.offsetX;
  const y = e.offsetY;

  // Send data over WebSocket
  const drawData: DrawData = { channel_id: channelId, x, y, prevX, prevY, line_color: color, line_width: lineWidth };
  sendWebsocketCommand("whiteboard", drawData)

  drawOnCanvas(x, y, prevX, prevY, color, lineWidth);

  prevX = x;
  prevY = y;
}

function stopDrawing(){
  drawing = false;
}


function drawOnCanvas(x: number, y: number, prevX: number, prevY: number, color: string, lineWidth: number){
  if (!ctx || prevX === undefined || prevY === undefined) return;

  ctx.beginPath();
  console.log(prevX, prevY, x, y);
  ctx.moveTo(prevX, prevY);
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.lineTo(x, y);
  ctx.stroke();
};


function setColor(newColor: string) {
  color = newColor;
  lineWidth = 1;

}
function eraseColor(newColor: string){
  color = newColor;
  lineWidth = 10;
}

</script>

<template>
  <div class="whiteboard">
    <canvas ref="canvas" width="1440" height="400" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing" class="canvas"></canvas> 
    <div class="tools">
      <button id="red" style="background-color: red" @click="setColor('red')"></button>
      <button id="blue" style="background-color: blue" @click="setColor('blue')"></button>
      <button id="blue2" style="background-color: #20a0e8" @click="setColor('#20a0e8')"></button>
      <button id="green" style="background-color: green" @click="setColor('green')"></button>
      <button id="yellow" style="background-color: yellow" @click="setColor('yellow')"></button>
      <button id="purple" style="background-color: purple" @click="setColor('purple')"></button>
      <button id="pink" style="background-color: #ff69b4" @click="setColor('#ff69b4')"></button>
      <button id="orange" style="background-color: orange" @click="setColor('orange')"></button>
      <button id="teal" style="background-color: teal" @click="setColor('teal')"></button>
      <button id="lime" style="background-color: #00ff00" @click="setColor('#00ff00')"></button>
      <button id="cyan" style="background-color: cyan" @click="setColor('cyan')"></button>
      <button id="indigo" style="background-color: indigo" @click="setColor('indigo')"></button>
      <button id="gold" style="background-color: gold" @click="setColor('gold')"></button>
      <button id="brown" style="background-color: brown" @click="setColor('brown')"></button>
      <button id="black" style="background-color: black" @click="setColor('black')"></button>
      <button id="white" style="background-color: white" @click="eraseColor('white')"></button>
    </div>  
  </div>
</template>

<style>
.tools{
  display: flex;
  flex-direction: column;
}

.whiteboard {
  display: flex;
  justify-content: center;
}

.tools button {
  width: 20px; 
  height: 20px;
}

</style>