import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

//创建存储对象

export default new Vuex.Store({
  // 需要存储的值都放在这里面
  state() {
    return {
      auth: null,
      role: 'none',
    }
  },
  // 在其他视图中通过 $store.commit('setState', 10) 使用，用于修改stor存的值
  mutations: {
    setAuth(state, datajson) { // 只能接受两个参数，用于修改store存的值
      state.auth = datajson.auth;
      state.role = datajson.role;
      state.expire = datajson.expire;
      state.name = datajson.name;
    },
    clearAuth(state) {
      state.auth = null;
      state.role = 'none';
    }
  },
  // 相当于组件的计算属性 通过 $store.getters.doubleCount 获取计算后的值
  getters: {},
  // 异步任务 不会改变state 通过 $store.dispath('doubleCount') 使用
  actions: {},
  // store的下级store 方便大型项目复杂数据管理，这里面相当于可以在放置一个和外面这些一样的模块
  modules: {},
});