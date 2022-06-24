<template>
  <div id="history">
    <h1>自习室预约</h1>

    <notification v-bind:notifications="notifications"></notification>

    <div v-if="is_booked">
      <p>你已经预约了自习室！点击签到查看详情。</p>
    </div>
    <div v-else>

      <div>
        <el-select v-model="selectedBuilding" placeholder="选择楼栋">
          <el-option v-for="i in buildingList" :key="i" :label="i" :value="i"></el-option>
        </el-select>
      </div>

      <div>
        <el-select v-model="selectedClassroom" placeholder="选择教室">
          <el-option v-for="i in classRoomList" :key="i" :label="i" :value="i"></el-option>
        </el-select>
      </div>

      <div>
        <el-select v-model="selectedStartTime" placeholder="选择预约起始时间">
          <el-option v-for="i, v in availableSeatList" v-if="i != -1"
            :key="v"
            :label="(v < 10 ? '0' : '') + v + ':00 余' + i + '人'"
            :value="v"
            :disabled="i <= 0"
          ></el-option>
        </el-select>
        <el-select v-model="selectedEndTime" placeholder="选择预约结束时间">
          <el-option v-for="i, v in availableSeatList" v-if="i != -1"
            :key="v"
            :label="(v < 9 ? '0' : '') + (v + 1) + ':00 余' + i + '人'"
            :value="v"
            :disabled="i <= 0"
          ></el-option>
        </el-select>
      </div>

      <div class="form-group">
        <button class="btn btn-success">预定</button>
      </div>
    </div>
      
  </div>
</template>

<script>
import Notification from "./notifications.vue";

import { backend_link } from "../const.vue";


export default {
  data() {
    return {
      originalStudyRooms: [
        {
          id: 1,
          buildingNumber: 'JB',
          classRoomNumber: 'JB101',
          startTime: 18,
          endTime: 22,
          seatNumber: 1,
          book: [
            { time: 18, emptyNumber: 1 },
            { time: 19, emptyNumber: 1 },
            { time: 20, emptyNumber: 0 },
            { time: 21, emptyNumber: 0 },
            { time: 22, emptyNumber: 1 },
          ]
        },
        {
          id: 1,
          buildingNumber: 'JB',
          classRoomNumber: 'JB102',
          startTime: 6,
          endTime: 9,
          seatNumber: 1,
          book: [
            { time: 6, emptyNumber: 1 },
            { time: 7, emptyNumber: 1 },
            { time: 8, emptyNumber: 0 },
            { time: 9, emptyNumber: 1 },
          ]
        },
        {
          id: 2,
          buildingNumber: 'JA',
          classRoomNumber: 'JA202',
          startTime: 10,
          endTime: 12,
          seatNumber: 2,
          book: [
            { time: 10, emptyNumber: 2 },
            { time: 11, emptyNumber: 1 },
            { time: 12, emptyNumber: 0 },
          ]
        }
      ],
      selectedBuilding: '',
      selectedClassroom: '',
      selectedStartTime: null,
      selectedEndTime: null,
    };
  },

  computed: {
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
      this.selectedClassroom = ''
      return arr
    },
    availableSeatList () {
      let arr = []
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding)
          if (i.classRoomNumber == this.selectedClassroom) {
            for (let j = 0; j < 24; j ++ )
              arr.push(-1)
            for (let j of i.book)
              arr[j.time] = j.emptyNumber
          }
      this.selectedStartTime = this.selectedEndTime = null 
      return arr
    }
  },

  created: function () {
    this.$http.get(backend_link + 'current_booking').then(
      (response) => {
        let data = response.data;
        this.is_booked = data.is_booked;
        if (data.is_booked) this.booking = data.booking;
      }
    )
  },

  methods: {
    
    book () {
      this.$http.post(backend_link + "book", {
        auth: '',
        buildingNumber: this.selectedBuilding,
        classRoomNumber: this.selectedClassroom,
        startTime: this.selectedStartTime,
        endTime: this.selectedEndTime
      }, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .then(
        (response) => {
          this.$router.push({ name: "checkin" });
        },
        (response) => {
          this.notifications.push({
            type: "danger",
            message: "预约失败 " + JSON.stringify(response),
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
