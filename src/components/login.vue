<template>
  <div id="login-account">
    <h1>登录</h1>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="login">
      <div class="form-group">
        <label name="account_name">用户名</label>
        <input
          type="text"
          class="form-control"
          v-model="account.name"
          id="account_name"
          required
        />
      </div>

      <div class="form-group">
        <label name="account_password">密码</label>
        <input
          type="password"
          class="form-control"
          v-model="account.password"
          id="account_password"
          required
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">登录</button>
      </div>
    </form>
  </div>
</template>


<style lang="css" scoped>
#login-account {
  display: flex;
  flex-direction: column;
  align-items: center;
}
#login-account > * {
  width: 400px;
}
</style>

<script>
import Notification from "./notifications.vue";

import { backend_link, success_proxy_timeout } from "../const.vue";
import store from "../store";


export default {
  data() {
    return {
      account: {},
      notifications: [],
    };
  },

  methods: {
    login: function () {
      this.$http
        .post(backend_link + "login", this.account, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then(
          (response) => {
            if (response.status)
            this.notifications.push({
              type: "success",
              message: "登录成功",
            });
            store.commit('setAuth', response.body);
            if (response.body.role == 'admin')
              setTimeout(() => {
                this.$router.push('/all_students')
              }, success_proxy_timeout)
            else if (response.body.role == 'user')
              setTimeout(() => {
                this.$router.push('/personal_info')
              }, success_proxy_timeout)
          },
          (response) => {
            this.notifications.push({
              type: "error",
              message: "登录失败 " + response.body.detail.error_msg,
            });
          }
        );
    },
  },

  components: {
    notification: Notification,
  },
};
</script>
