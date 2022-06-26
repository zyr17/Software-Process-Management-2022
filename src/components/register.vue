<template>
  <div id="register">
    <h1>注册</h1>

    <!-- <p>
      <router-link :to="{ name: 'all_students' }"
        >返回学生信息列表页面</router-link
      >
    </p> -->

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="register">
      <div class="form-group" style="display: none">
        <label name="student_id">ID (自动生成, 无需填写)</label>
        <input
          type="text"
          class="form-control"
          disabled
          v-model="student.id"
          id="student_id"
        />
      </div>

      <div class="form-group">
        <label name="student_number">学号</label>
        <input
          type="text"
          class="form-control"
          v-model="student.stuNum"
          id="student_number"
          required
        />
      </div>

      <div class="form-group">
        <label name="student_name">用户名</label>
        <input
          type="text"
          class="form-control"
          v-model="student.name"
          id="student_name"
          required
        />
      </div>

      <div class="form-group">
        <label name="student_password">密码</label>
        <input
          type="password"
          class="form-control"
          v-model="student.password"
          id="student_password"
          required
        />
      </div>

      <div class="form-group">
        <label name="student_password_1">再次输入密码</label>
        <input
          type="password"
          class="form-control"
          v-model="student.password2"
          id="student_password_1"
          required
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">注册</button>
      </div>
    </form>
  </div>
</template>

<style lang="css" scoped>
#register {
  display: flex;
  flex-direction: column;
  align-items: center;
}
#register > * {
  width: 400px;
}
</style>

<script>
import Notification from "./notifications.vue";

import { backend_link, success_proxy_timeout } from "../const.vue";


export default {
  data() {
    return {
      student: {},
      notifications: [],
    };
  },

  methods: {
    register: function () {
      if (this.student.password != this.student.password2) {
        this.notifications.push({
          type: "danger",
          message: "两次密码不一致",
        });
        return;
      }
      this.$http
        .post(backend_link + "user", this.student, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then(
          (response) => {
            this.notifications.push({
              type: "success",
              message: "学生注册成功",
            });
            setTimeout(() => {
              this.$router.push('/login')
            }, success_proxy_timeout)
          },
          (response) => {
            this.notifications.push({
              type: "danger",
              message: "学生注册失败 " + response.body.detail.error_msg,
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
