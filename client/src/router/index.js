import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Train from '../views/train/train.vue'
import Inference from '../views/inference/inference.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/train',
    name: 'Train',
    component: Train
  },
  {
    path: '/inference',
    name: 'Inference',
    component: Inference
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
