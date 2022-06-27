<template>
  <div id="edit-student">
    <h1 v-if="is_edit">用户 {{ student.name }} 信息修改</h1>
    <h1 v-else>用户信息添加</h1>

    <p>
      <router-link :to="{ name: 'all_students' }"
        >返回用户信息列表页面</router-link
      >
    </p>

    
    <form v-on:submit.prevent="editStudent">
      <div class="form-group">
        <label name="student_id">ID</label>
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
          v-model="student.newPassword"
          id="student_password"
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">提交</button>
      </div>
    </form>
  </div>
</template>

<style lang="css" scoped>
#edit-student {
  display: flex;
  flex-direction: column;
  align-items: center;
}
#edit-student > * {
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
      student: {},
      notifications: [],
      is_edit: true
    };
  },

  created: function () {
    this.is_edit = this.getStudent();
  },
  
  computed: {
    mode_str() {
      return this.is_edit ? '修改' : '添加';
    }
  },

  methods: {
    getStudent: function () {
      let input_data = this.$route.params.stu;
      if (input_data) this.student = input_data;
      else return false;
      return true;
    },

    editStudent: function () {
      this.$http
        .put(backend_link + "user/" + this.student.id, this.student, {
          headers: {
            "Auth-Token": store.state.auth
          },
        })
        .then(
          (response) => {
            store.commit('setNotification', {
              type: "success",
              message: "用户信息" + this.mode_str + "成功",
            });
            setTimeout(() => {
              this.$router.push('/all_students')
            }, success_proxy_timeout)
          },
          (response) => {
            store.commit('setNotification', {
              type: "danger",
              message: "用户信息" + this.mode_str + "失败",
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
