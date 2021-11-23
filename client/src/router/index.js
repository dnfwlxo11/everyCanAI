import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Inference from '../views/inference/inference.vue'
import Train from '../views/train/train.vue'
import Models from '../views/repository/models.vue'

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
    path: '/models',
    name: 'Models',
    component: Models
  },
  {
    path: '/inference',
    name: 'Inference',
    component: Inference
  }
]

const router = new VueRouter({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes
})

export default router
