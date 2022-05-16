<template>
  <div id="all_students">
    <h1>学生管理</h1>

    <!-- <p>
      <router-link :to="{ name: 'edit_student' }" class="btn btn-primary"
        >添加学生信息</router-link>
    </p> -->

    <div class="form-group">
      <input
        type="text"
        name="search"
        v-model="studentSearch"
        placeholder="Search Students"
        class="form-control"
      />
    </div>

    <table class="table table-hover">
      <thead>
        <tr>
          <td>ID</td>
          <td>学号</td>
          <td>姓名</td>
          <td>操作</td>
        </tr>
      </thead>

      <tbody>
        <tr v-for="student in students">
          <td>{{ student.id }}</td>
          <td>{{ student.stuNum }}</td>
          <td>{{ student.name }}</td>
          <td>
            <router-link
              :to="{ name: 'edit_student', params: { stu: student } }"
              class="btn btn-primary"
              >修改</router-link
            >
            <button
              @click="deleteStudent"
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

export default {
  data() {
    return {
      originalStudents: [
        {
          id: 1,
          stuNum: 123456,
          name: 'zhangsan'
        },
        {
          id: 2,
          stuNum: 654321,
          name: 'lisi'
        }
      ],
      studentSearch: "",
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
      this.$http.get(backend_link + "student").then(
        (response) => {
          this.originalStudents = response.body;
        },
        (response) => {}
      );
    },
    deleteStudent: function () {
      this.$http
        .delete(backend_link + "student/" + this.student.stuNum, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then(
          (response) => {
            this.$router.push({ name: "all_students" });
          },
          (response) => {
            this.notifications.push({
              type: "danger",
              message: "学生信息无法删除",
            });
          }
        );
    }
  },
};
</script>
