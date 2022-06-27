<template>
  <div id="all_students">
    <h1>用户管理</h1>

    <!-- <p>
      <router-link :to="{ name: 'edit_student' }" class="btn btn-primary"
        >添加学生信息</router-link>
    </p> -->

    <div class="form-group">
      <input
        type="text"
        name="search"
        v-model="studentSearch"
        placeholder="根据用户名搜索"
        class="form-control"
      />
    </div>

    <table class="table table-hover">
      <thead>
        <tr>
          <td>ID</td>
          <td>学号</td>
          <td>用户名</td>
          <td>角色</td>
          <td>操作</td>
        </tr>
      </thead>

      <tbody>
        <tr v-for="student in students">
          <td>{{ student.id }}</td>
          <td>{{ student.stuNum }}</td>
          <td>{{ student.name }}</td>
          <td>{{ role2name(student.role) }}</td>
          <td>
            <router-link
              :to="{ name: 'edit_student', params: { stu: student } }"
              class="btn btn-primary"
              >修改</router-link
            >
            <button
              @click="deleteStudent(student.id)"
              class="btn btn-danger"
              >删除</button
            >
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

import { backend_link } from "../const.vue"
import store from '../store'

export default {
  data() {
    return {
      originalStudents: [
        // {
        //   id: 1,
        //   stuNum: 123456,
        //   name: 'zhangsan',
        //   role: 'admin'
        // },
        // {
        //   id: 2,
        //   stuNum: 654321,
        //   name: 'lisi',
        //   role: 'user'
        // }
      ],
      studentSearch: "",
      notifications: []
    };
  },

  created: function () {
    this.fetchStudentData();
  },
  
  computed: {
    students() {
      if (this.studentSearch == "") {
        return this.originalStudents;
      }

      var searchedStudents = [];
      for (var i = 0; i < this.originalStudents.length; i++) {
        var studentName = this.originalStudents[i]["name"].toLowerCase();
        if (studentName.indexOf(this.studentSearch.toLowerCase()) >= 0) {
          searchedStudents.push(this.originalStudents[i]);
        }
      }
      return searchedStudents;
    }
  },

  methods: {
    fetchStudentData: function () {
      this.$http.get(backend_link + "user", {
        headers: {
          "Auth-Token": store.state.auth
        }
      }).then(
        (response) => {
          this.originalStudents = response.body;
        },
        (response) => {}
      );
    },
    deleteStudent: function (userid) {
      this.$http
        .delete(backend_link + "user/" + userid, {
          headers: {
            "Auth-Token": store.state.auth
          },
        })
        .then(
          (response) => {
            store.commit('setNotification', {
              type: "success",
              message: "用户删除成功"
            });
            this.fetchStudentData()
          },
          (response) => {
            store.commit('setNotification', {
              type: "danger",
              message: "用户删除失败 " + JSON.stringify(response.body.detail),
            });
          }
        );
    },
    role2name: function (role) {
      return {
        'admin': '管理员',
        'user': '普通用户'
      }[role]
    }
  },
};
</script>
