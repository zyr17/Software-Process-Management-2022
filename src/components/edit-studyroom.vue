<template>
  <div id="edit-studyroom">
    <h1 v-if="is_edit">自习室 {{ studyroom.buildingNumber }} {{ studyroom.classRoomNumber }} 信息修改</h1>
    <h1 v-else>自习室信息添加</h1>

    <p>
      <router-link :to="{ name: 'all_studyrooms' }"
        >返回自习室信息列表页面</router-link>
    </p>

    <notification v-bind:notifications="notifications"></notification>

    <form v-on:submit.prevent="editstudyroom">
      <div class="form-group">
        <label name="studyroom_id">ID</label>
        <input
          type="text"
          class="form-control"
          disabled
          v-model="studyroom.id"
          id="studyroom_id"
        />
      </div>

      <div class="form-group">
        <label name="studyroom_buildingnumber">楼栋信息</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.buildingNumber"
          id="studyroom_buildingnumber"
          required
        />
      </div>

      <div class="form-group">
        <label name="studyroom_classroomnumber">自习室房间号</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.classRoomNumber"
          id="studyroom_classroomnumber"
          required
        />
      </div>

      <div class="form-group">
        <label name="studyroom_starttime">可预约开始时间</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.startTime"
          id="studyroom_starttime"
          required
        />
      </div>

      <div class="form-group">
        <label name="studyroom_endtime">可预约结束时间</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.endTime"
          id="studyroom_endtime"
          required
        />
      </div>

      <div class="form-group">
        <button class="btn btn-primary">提交</button>
      </div>
    </form>
  </div>
</template>

<script>
import Notification from "./notifications.vue";

import backend_link from "../const.vue";

export default {
  data() {
    return {
      studyroom: {},
      notifications: [],
      is_edit: true
    };
  },

  created: function () {
    this.is_edit = this.getStudyRoom();
  },
  
  computed: {
    mode_str() {
      return this.is_edit ? '修改' : '添加';
    }
  },

  methods: {
    getStudyRoom: function () {
      let input_data = this.$route.params.studyroom;
      if (input_data) this.studyroom = input_data;
      else return false;
      return true;
    },

    editstudyroom: function () {
      this.$http
        .put(backend_link + "studyroom", this.studyroom, {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then(
          (response) => {
            this.notifications.push({
              type: "success",
              message: "自习室信息" + this.mode_str + "成功",
            });
          },
          (response) => {
            this.notifications.push({
              type: "error",
              message: "自习室信息" + this.mode_str + "失败",
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
