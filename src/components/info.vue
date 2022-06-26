<template>
  <div id="info">
    <h1>个人信息</h1>

    <!-- <p>
      <router-link :to="{ name: 'all_students' }"
        >返回学生信息列表页面</router-link
      >
    </p> -->

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="update_info">
      <div class="form-group">
        <label name="student_id">ID (无法修改)</label>
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
        <label name="current_password">现在密码</label>
        <input
          type="password"
          class="form-control"
          v-model="student.currentPassword"
          id="current_password"
          required
        />
      </div>

      <div class="form-group">
        <label name="student_password">更新密码</label>
        <input
          type="password"
          class="form-control"
          v-model="student.newPassword"
          id="student_password"
        />
      </div>

      <div class="form-group">
        <label name="student_password_1">再次输入密码</label>
        <input
          type="password"
          class="form-control"
          v-model="student.password2"
          id="student_password_1"
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">更新</button>
      </div>
    </form>
  </div>
</template>

<style lang="css" scoped>
#info {
  display: flex;
  flex-direction: column;
  align-items: center;
}
#info > * {
  width: 400px;
}
</style>

<script>
import Notification from "./notifications.vue";

import { backend_link, success_proxy_timeout } from "../const.vue";
import store from '../store';


export default {
  data() {
    return {
      student: {},
      notifications: [],
    };
  },

  created: function () {
    this.fetch_info();
  },

  methods: {
    fetch_info: function () {
      this.$http.get(backend_link + "user/" + store.state.id, {
        headers: {
          "Auth-Token": store.state.auth
        }
      }).then(
        (response) => {
          this.student = response.body;
        },
        (response) => {}
      );
    },
    update_info: function () {
      if (this.student.newPassword != this.student.password2) {
        this.notifications.push({
          type: "error",
          message: "两次密码不一致",
        });
        return;
      }
      this.$http
        .put(backend_link + "user/" + store.state.id, this.student, {
          headers: {
            'Auth-Token': store.state.auth
          },
        })
        .then(
          (response) => {
            this.notifications.push({
              type: "success",
              message: "信息更新成功",
            });
            setTimeout(() => {
              this.$router.go(0)
            }, success_proxy_timeout)
          },
          (response) => {
            this.notifications.push({
              type: "error",
              message: "信息更新失败" + JSON.stringify(response.body.detail),
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
