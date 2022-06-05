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
          <td>可预约时间</td>
        </tr>
      </thead>

      <tbody>
        <tr v-for="studyRoom in studyRooms">
          <td>{{ studyRoom.id }}</td>
          <td>{{ studyRoom.buildingNumber }}</td>
          <td>{{ studyRoom.classRoomNumber }}</td>
          <td>{{ studyRoom.startTime }}-{{ studyRoom.endTime }}</td>
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

import backend_link from "../const.vue";

export default {
  data() {
    return {
      originalStudyRooms: [
        {
          id: 1,
          buildingNumber: 'JB',
          classRoomNumber: 'JB101',
          startTime: '08:00',
          endTime: '22:00',
        },
        {
          id: 2,
          buildingNumber: 'JA',
          classRoomNumber: 'JA202',
          startTime: '10:30',
          endTime: '12:00',
        }
      ],
      studyRoomsSearch: "",
    };
  },

  created: function () {
    this.$http.get(backend_link + 'studyroom', {}).then(
      (response) => {
        this.originalStudyRooms = response.data;
      }
    )
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
    del_room(room_id) {
      this.$http.delete(backend_link + 'studyroom', { id: room_id }).then(
        (response) => {
          this.originalStudyRooms = response.data;
        }
      )
    }
  },
};
</script>
