<template>
  <div id="history">
    <h1>刷卡签到</h1>

    
    <div>

      <div>
        <el-select v-model="selectedBuilding" placeholder="选择楼栋">
          <el-option 
            v-for="i in buildingList" 
            :key="i" 
            :label="i" 
            :value="i"
          ></el-option>
        </el-select>
      </div>

      <div>
        <el-select v-model="selectedClassroom" placeholder="选择教室">
          <el-option v-for="i in classRoomList" :key="i" :label="i" :value="i"></el-option>
        </el-select>
      </div>

      <form v-on:submit.prevent="checkin">
        <div class="form-group">
          <label name="card_id">卡号</label>
          <input
            type="text"
            class="form-control"
            v-model="userId"
            placeholder="刷卡自动填写(手动填写用户ID)"
            id="card_id"
            required
          />
        </div>

        <div class="form-group">
          <button class="btn btn-success">刷卡签到</button>
        </div>
      </form>
    </div>
      
  </div>
</template>

<script>
import Notification from "./notifications.vue";

import { backend_link } from "../const.vue";

import store from '../store';

export default {
  data() {
    return {
      originalStudyRooms: [],
      selectedBuilding: '',
      selectedClassroom: '',
      buildingNumber: '',
      classRoomNumber: '',
      notifications: [],
      userId: '',
    };
  },
  
  created: function () {
    this.$http.get(backend_link + 'studyroom', {
      headers: {
        'Auth-Token': store.state.auth
      }
    }).then(
      (response) => {
        let data = response.data;
        this.originalStudyRooms = data;
      }
    )
  },

  computed: {
    selectedId () {
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding
            && i.classRoomNumber == this.selectedClassroom)
          return i.id
      return null
    },
    buildingList () {
      let arr = [];
      for (let i of this.originalStudyRooms)
        arr.push(i.buildingNumber)
      arr = Array.from(new Set(arr))
      arr.sort()
      return arr
    },
    classRoomList () {
      let arr = [];
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding)
          arr.push(i.classRoomNumber)
      arr = Array.from(new Set(arr))
      arr.sort()
      if (arr.indexOf(this.selectedClassroom) == -1)
        this.selectedClassroom = ''
      return arr
    },
  },

  methods: {
    checkin () {
      this.$http.post(backend_link + "card_checkin", {
        roomId: this.selectedId,
        userId: this.userId,
      }, {
        headers: {
          'Auth-Token': store.state.auth
        },
      })
      .then(
        (response) => {
          response = response.data
          console.log(response)
          let text = response.userName + ' '
                     + '时间 ' + this.to_date(response.date) + ' ' + this.to_time(response.startTime) + '-' + this.to_time(response.endTime);
          store.commit('setNotification', {
            type: "success",
            message: "签到成功\n" + text,
          });
        },
        (response) => {
          store.commit('setNotification', {
            type: "danger",
            message: "签到失败 " + JSON.stringify(response.body.detail),
          });
        }
      );
    },
    to_date(i) {
      let date = new Date(i * 1000 * 86400)
      return date.getFullYear() + '.' + (date.getMonth() + 1) + '.' + date.getDate()
    },
    to_time(i) {
      return (i < 10 ? '0' : '') + (i) + ':00';
    },
  },

  components: {
    notification: Notification,
  },
};
</script>
