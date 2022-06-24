import Vue from 'vue'

import VueRouter from 'vue-router'
Vue.use(VueRouter)

import VueResource from 'vue-resource';
Vue.use(VueResource);

import ElementUI from 'element-ui';
Vue.use(ElementUI)

import App from './App.vue'

const AllStudents = require('./components/all-students.vue');
const Register = require('./components/register.vue');
const Info = require('./components/info.vue');
const EditStudent = require('./components/edit-student.vue');
const EditStudyRoom = require('./components/edit-studyroom.vue');
const AllStudyRooms = require('./components/all-studyrooms.vue');
const Login = require('./components/login.vue');
const History = require('./components/history.vue')
const Checkin = require('./components/checkin.vue')
const CardCheckin = require('./components/card-checkin.vue')
const Book = require('./components/book.vue')

const routes = [
    {
        name: 'welcome',
        path: '/',
        component: Login
    },
    {
        name: 'register',
        path: '/register',
        component: Register
    },
    {
        name: 'login',
        path: '/login',
        component: Login
    },
    {
        name: 'info',
        path: '/personal_info',
        component: Info
    },
    {
        name: 'book',
        path: '/book',
        component: Book
    },
    {
        name: 'checkin',
        path: '/checkin',
        component: Checkin
    },
    {
        name: 'card_checkin',
        path: '/card_checkin',
        component: CardCheckin
    },
    {
        name: 'history',
        path: '/history',
        component: History
    },
    {
        name: 'all_students',
        path: '/all_students',
        component: AllStudents
    },
    {
        name: 'edit_student',
        path: '/student/edit/:stu',
        component: EditStudent
    },
    {
        name: 'all_studyrooms',
        path: '/all_studyrooms',
        component: AllStudyRooms
    },
    {
        name: 'edit_studyroom',
        path: '/studyroom/edit/:studyroom',
        component: EditStudyRoom
    },
];
var router = new VueRouter({ routes: routes, mode: 'history' });
new Vue(Vue.util.extend({ router }, App)).$mount('#app');