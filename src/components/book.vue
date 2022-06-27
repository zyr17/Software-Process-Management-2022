<template>
  <div id="history">
    <h1>自习室预约</h1>

    
    <div v-if="is_booked">
      <p>你已经预约了自习室！点击签到查看详情。</p>
    </div>
    <div v-else>

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

      <div>
        <p>选择预约日期 当前选择日期为 {{ to_date(new Date(selectedDate).getTime() / 1000 / 86400) }}</p>
        <p :style="availableDateRange ? '' : 'visibility: hidden'">
          当前教室可选预约日期为 {{ availableDateRange ? availableDateRange[0] : '' }} - {{ availableDateRange ? availableDateRange[1] : '' }}
        </p>
        <el-calendar v-model="selectedDate">
        </el-calendar>
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
        <button class="btn btn-success" @click="random">随机选择</button>
        <button class="btn btn-success" @click="quick">快速选择</button>
        <button class="btn btn-success" @click="book">预约</button>
      </div>
    </div>
      
  </div>
</template>

<script>

import { backend_link, success_proxy_timeout } from "../const.vue";
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
        //   id: 1,
        //   buildingNumber: 'JB',
        //   classRoomNumber: 'JB102',
        //   startTime: 6,
        //   endTime: 9,
        //   seatNumber: 1,
        //   book: [
        //     { time: 6, emptyNumber: 1 },
        //     { time: 7, emptyNumber: 1 },
        //     { time: 8, emptyNumber: 0 },
        //     { time: 9, emptyNumber: 1 },
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
      selectedBuilding: '',
      selectedClassroom: '',
      selectedDate: new Date(),
      selectedStartTime: null,
      selectedEndTime: null,
      notifications: [],
    };
  },

  computed: {
    selectedId () {
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding
            && i.classRoomNumber == this.selectedClassroom)
          return i.id
      return null
    },
    availableDateRange () {
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding
            && i.classRoomNumber == this.selectedClassroom) {
          let current_date = parseInt(new Date(this.selectedDate).getTime() / 1000 / 86400)
          // if (current_date < i.startDate || current_date > i.endDate)
          //   this.selectedDate = i.startDate * 1000 * 86400
          return [this.to_date(i.startDate), this.to_date(i.endDate)]
        }
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
    availableSeatList () {
      let arr = []
      for (let i of this.originalStudyRooms)
        if (i.buildingNumber == this.selectedBuilding)
          if (i.classRoomNumber == this.selectedClassroom) {
            let current_date = parseInt(new Date(this.selectedDate).getTime() / 1000 / 86400)
            arr = this.get_remain_arr(i, current_date)
          }
      if (arr[this.selectedStartTime] <= 0)
        this.selectedStartTime = null
      if (arr[this.selectedEndTime] <= 0)
        this.selectedEndTime = null
      return arr
    }
  },

  created: function () {
    this.$http.get(backend_link + 'book/' + store.state.id, {
      headers: {
        'Auth-Token': store.state.auth
      }
    }).then(
      (response) => {
        let data = response.data;
        this.is_booked = true;
        this.booking = data.booking;
      },
      (response) => {
        if (response.status == 404) {
          this.is_booked = false;
        }
        else {
          store.commit('setNotification', {
            type: "danger",
            message: "查询当前预约情况失败 " + JSON.stringify(response.body.detail),
          });
        }
      }
    )
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

  methods: {
    
    book () {
      let postdate = parseInt(new Date(this.selectedDate).getTime() / 86400 / 1000)
      if (!this.availableDateRange || this.to_date(postdate) < this.availableDateRange[0] || this.to_date(postdate) > this.availableDateRange[1]) {
        alert('日期范围未初始化或所选日期不在范围内')
        return
      }
      this.$http.post(backend_link + "book/" + store.state.id, {
        roomId: this.selectedId,
        date: postdate,
        startTime: this.selectedStartTime,
        endTime: this.selectedEndTime
      }, {
        headers: {
          'Auth-Token': store.state.auth
        },
      })
      .then(
        (response) => {
          store.commit('setNotification', {
            type: "success",
            message: "预约成功"
          });
          setTimeout(() => {
            this.$router.push({ name: "checkin" });
          }, success_proxy_timeout)
        },
        (response) => {
          store.commit('setNotification', {
            type: "danger",
            message: "预约失败 " + JSON.stringify(response.body.detail),
          });
        }
      );
    },
    random() {
      function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [array[i], array[j]] = [array[j], array[i]];
        }
        return array
      }
      let shuffle_room = shuffle(this.originalStudyRooms.slice())
      let current_date = new Date(this.selectedDate).getTime() / 1000 / 86400
      for (let i of shuffle_room) {
        if (current_date < i.startDate || current_date > i.endDate)
          continue
        let remain_arr = this.get_remain_arr(i, current_date)
        for (let j = 0; j < remain_arr.length; j ++ )
          if (remain_arr[j] > 0) {
            this.selectedBuilding = i.buildingNumber
            this.selectedClassroom = i.classRoomNumber
            this.selectedStartTime = j
            this.selectedEndTime = j
            return
          }
      }
      alert('没有在所选日期找到能够预约的自习室！')
    },
    quick() {
      this.selectedDate = new Date()
      let current = parseInt(new Date().getHours())
      let date = parseInt(new Date().getTime() / 1000 / 86400)
      for (let i of this.originalStudyRooms) {
        if (date < i.startDate || date > i.endDate)
          continue
        let remain_arr = this.get_remain_arr(i, date)
        console.log(date, i, remain_arr)
        if (remain_arr[current] > 0) {
          this.selectedBuilding = i.buildingNumber
          this.selectedClassroom = i.classRoomNumber
          this.selectedStartTime = current
          this.selectedEndTime = current
          return
        }
      }
      alert('没有找到当前时间能够预约的自习室！')
    },
    to_date(i) {
      let date = new Date(i * 1000 * 86400)
      return date.getFullYear() + '.' + (date.getMonth() + 1) + '.' + date.getDate()
    },
    get_remain_arr(i, current_date) {
      let arr = []
      for (let j = 0; j < 24; j ++ )
        arr.push(-1)
      for (let j = i.startTime; j <= i.endTime; j ++ )
        arr[j] = i.seatNumber
      for (let book of i.book)
        if (book.date == current_date) {
          for (let k = book.startTime; k <= book.endTime; k ++ )
            arr[k] --
        }
      return arr
    }
  },

  components: {
  },
};
</script>
