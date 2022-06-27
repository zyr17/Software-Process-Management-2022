import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

//创建存储对象

export default new Vuex.Store({
  // 需要存储的值都放在这里面
  state() {
    let res = {
      auth: localStorage.getItem('auth'),
      role: localStorage.getItem('role') || 'none',
      expire: localStorage.getItem('expire') || 0,
      name: localStorage.getItem('name'),
      id: localStorage.getItem('id'),
    }
    if (res.expire < (new Date()).getTime() / 1000) {
      if (res.expire)
        console.log('token expired')
      let current_page = window.location.href
      let mainpage = /https?:\/\/[^\/]*\//.exec(current_page)[0]
      console.log(window.location.href, mainpage)
      if (window.location.href != mainpage)
        window.location.href = mainpage
      res = { auth: null, role: 'none', expire: 0, name: null, id: null }
    }
    res.notifications = []
    return res
  },
  // 在其他视图中通过 $store.commit('setState', 10) 使用，用于修改stor存的值
  mutations: {
    setAuth(state, datajson) { // 只能接受两个参数，用于修改store存的值
      state.auth = datajson.auth;
      state.role = datajson.role;
      state.expire = datajson.expire;
      state.name = datajson.name;
      state.id = datajson.id;
      localStorage.setItem('auth', datajson.auth)
      localStorage.setItem('role', datajson.role)
      localStorage.setItem('expire', datajson.expire)
      localStorage.setItem('name', datajson.name)
      localStorage.setItem('id', datajson.id)
    },
    clearAuth(state) {
      state.auth = null;
      state.role = 'none';
    },
    setNotification(state, data) {  // 添加提醒，同时加入时间戳
      data.notification_time = new Date()
      state.notifications.push(data)
    }
  },
  // 相当于组件的计算属性 通过 $store.getters.doubleCount 获取计算后的值
  getters: {},
  // 异步任务 不会改变state 通过 $store.dispath('doubleCount') 使用
  actions: {},
  // store的下级store 方便大型项目复杂数据管理，这里面相当于可以在放置一个和外面这些一样的模块
  modules: {},
});