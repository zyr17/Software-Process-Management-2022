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
      <div class="form-group" style="display: inherit">
        <label name="studyroom_id">ID (无法修改)</label>
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
        <label name="studyroom_seatnumber">自习室座位数</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.seatNumber"
          id="studyroom_seatnumber"
          required
        />
      </div>

      <div class="form-group">
        <label name="studyroom_starttime">可预约开始日期</label>
        <el-calendar v-model="studyroom.startDate">
        </el-calendar>
      </div>

      <div class="form-group">
        <label name="studyroom_starttime">可预约结束日期</label>
        <el-calendar v-model="studyroom.endDate">
        </el-calendar>
      </div>

      <div class="form-group">
        <label name="studyroom_starttime">可预约开始时间</label>
        <el-select v-model="studyroom.startTime" placeholder="请选择">
          <el-option
            v-for="i in 24" :key="i"
            :label="(i <= 10 ? '0' : '') + (i - 1) + ':00'"
            :value="i - 1"
          >
          </el-option>
        </el-select>

        <!-- <label name="studyroom_starttime">可预约开始时间</label>
        <input
          type="text"
          class="form-control"
          v-model="studyroom.startTime"
          id="studyroom_starttime"
          required
        /> -->
      </div>

      <div class="form-group">
        <label name="studyroom_starttime">可预约结束时间</label>
        <el-select v-model="studyroom.endTime" placeholder="请选择">
          <el-option
            v-for="i in 24" :key="i"
            :label="(i < 10 ? '0' : '') + (i) + ':00'"
            :value="i - 1"
          >
          </el-option>
        </el-select>
      </div>

      <div class="form-group">
        <button class="btn btn-primary">提交</button>
      </div>
    </form>
  </div>
</template>

<style lang="css" scoped>
#edit-studyroom {
  display: flex;
  flex-direction: column;
  align-items: center;
}
#edit-studyroom > * {
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
      if (input_data) {
        // change date number
        input_data.startDate *= 1000 * 86400
        input_data.endDate *= 1000 * 86400
        this.studyroom = input_data;
      }
      else return false;
      return true;
    },

    editstudyroom: function () {
      let promise = null
      let upload_data = JSON.parse(JSON.stringify(this.studyroom))
      console.log(this.studyroom, upload_data)
      upload_data.startDate = parseInt(new Date(upload_data.startDate).getTime() / 86400 / 1000)
      upload_data.endDate = parseInt(new Date(upload_data.endDate).getTime() / 86400 / 1000)
      if (this.is_edit)
        promise = this.$http
          .put(backend_link + "studyroom/" + this.studyroom.id, upload_data, {
            headers: {
              'Auth-Token': store.state.auth
            },
          })
      else
        promise = this.$http
          .post(backend_link + "studyroom", upload_data, {
            headers: {
              'Auth-Token': store.state.auth
            },
          })

      promise.then(
          (response) => {
            this.notifications.push({
              type: "success",
              message: "自习室信息" + this.mode_str + "成功",
            });
            setTimeout(() => {
              this.$router.push('/all_studyrooms')
            }, success_proxy_timeout)
          },
          (response) => {
            this.notifications.push({
              type: "danger",
              message: "自习室信息" + this.mode_str + "失败 " + 
                       JSON.stringify(response.body.detail),
            });
          }
        );
    },
  },

  components: {
    notification: Notification,
    // ElSelect: ElSelect,
    // ElOption: ElOption,
  },
};
</script>
