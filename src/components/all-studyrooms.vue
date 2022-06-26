<template>
  <div id="all-studyrooms">
    <h1>自习室管理</h1>

    <p>
      <router-link :to="{ name: 'edit_studyroom' }" class="btn btn-primary"
        >添加自习室</router-link>
    </p>

    <div class="form-group">
      <input
        type="text"
        name="search"
        v-model="studyRoomsSearch"
        placeholder="根据自习室搜索"
        class="form-control"
      />
    </div>

    <table class="table table-hover">
      <thead>
        <tr>
          <td>ID</td>
          <td>楼栋信息</td>
          <td>自习室信息</td>
          <td>座位数</td>
          <td>可预约日期</td>
          <td>可预约时间</td>
        </tr>
      </thead>

      <tbody>
        <tr v-for="studyRoom in studyRooms">
          <td>{{ studyRoom.id }}</td>
          <td>{{ studyRoom.buildingNumber }}</td>
          <td>{{ studyRoom.classRoomNumber }}</td>
          <td>{{ studyRoom.seatNumber }}</td>
          <td>{{ to_date(studyRoom.startDate) }} - {{ to_date(studyRoom.endDate) }}</td>
          <td>{{ to_time(studyRoom.startTime) }} - {{ to_time(studyRoom.endTime + 1) }}</td>
          <td>
            <router-link
              :to="{ name: 'edit_studyroom', params: { studyroom: studyRoom } }"
              class="btn btn-primary"
              >修改</router-link
            >
            <button @click="del_room(studyRoom.id)" class="btn btn-danger">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

import { backend_link } from "../const.vue";
import store from '../store';

export default {
  data() {
    return {
      originalStudyRooms: [
        // {
        //   id: 1,
        //   buildingNumber: 'JB',
        //   classRoomNumber: 'JB101',
        //   startTime: 18,
        //   endTime: 22,
        //   seatNumber: 1,
        //   book: [
        //     { time: 18, emptyNumber: 1 },
        //     { time: 19, emptyNumber: 1 },
        //     { time: 20, emptyNumber: 0 },
        //     { time: 21, emptyNumber: 0 },
        //     { time: 22, emptyNumber: 1 },
        //   ]
        // },
        // {
        //   id: 2,
        //   buildingNumber: 'JA',
        //   classRoomNumber: 'JA202',
        //   startTime: 10,
        //   endTime: 12,
        //   seatNumber: 2,
        //   book: [
        //     { time: 10, emptyNumber: 2 },
        //     { time: 11, emptyNumber: 1 },
        //     { time: 12, emptyNumber: 0 },
        //   ]
        // }
      ],
      studyRoomsSearch: "",
      notifications: [],
    };
  },

  created: function () {
    this.fetch_study_room()
  },
  
  computed: {
    studyRooms() {
      if (this.studyRoomsSearch == "") {
        return this.originalStudyRooms;
      }

      var searchedStudyRooms = [];
      for (var i = 0; i < this.originalStudyRooms.length; i++) {
        var roomName = this.originalStudyRooms[i]["classRoomNumber"].toLowerCase();
        if (roomName.indexOf(this.studyRoomsSearch.toLowerCase()) >= 0) {
          searchedStudyRooms.push(this.originalStudyRooms[i]);
        }
      }
      return searchedStudyRooms;
    }
  },

  methods: {
    fetch_study_room () {
      this.$http.get(backend_link + 'studyroom', {
        headers: {
          'Auth-Token': store.state.auth
        }
      }).then(
        (response) => {
          this.originalStudyRooms = response.body;
        },
        (response) => {}
      )
    },
    del_room(room_id) {
      this.$http.delete(backend_link + 'studyroom/' + room_id, {
        headers: {
          'Auth-Token': store.state.auth
        }
      }).then(
          (response) => {
            this.notifications.push({
              type: "success",
              message: "自习室删除成功",
            });
            this.fetch_study_room()
          }, 
          (response) => {
            this.notifications.push({
              type: "danger",
              message: "自习室删除失败" + JSON.stringify(response.body.detail),
            });
          }
      )
    },
    to_date(i) {
      let date = new Date(i * 1000 * 86400)
      return date.getFullYear() + '.' + (date.getMonth() + 1) + '.' + date.getDate()
    },
    to_time(i) {
      return (i < 10 ? '0' : '') + (i) + ':00';
    }
  },
};
</script>
