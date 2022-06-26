<template>
  <div id="history">
    <h1>预定详情和签到</h1>

    <!-- <p>
      <router-link :to="{ name: 'all_students' }"
        >返回学生信息列表页面</router-link
      >
    </p> -->

    <notification v-bind:notifications="notifications"></notification>

    <div v-if="!is_booked">
      <p>你目前还没有预定！点击预约前往预约。</p>
    </div>
    <div v-else>
      <p>预约教室：{{ booking.buildingNumber }} {{ booking.classRoomNumber }}</p>
      <!-- <p>座位号：{{ booking.seatNumber }}</p> -->
      <p>预约时间：{{ new Date(booking.bookTimeStamp * 1000.) }}</p>
      <p>自习时间：{{ to_date(booking.date) }} {{ to_time(booking.startTime) }}-{{ to_time(booking.endTime + 1) }}</p>

      <form v-on:submit.prevent="checkin">
        <div class="form-group">
          <label name="current_position">当前地理位置</label>
          <input
            type="text"
            class="form-control"
            v-model="current_position"
            placeholder="点击获取地理位置(未实现点击)"
            id="current_position"
            required
          />
        </div>

        <div class="form-group">
          <button class="btn btn-success">签到</button>
        </div>
      </form>
      <button @click="cancel" class="btn btn-danger">取消预定</button>
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
      booking: {
        // id: 1,
        // buildingNumber: 'JB',
        // classRoomNumber: '101',
        // seatNumber: '25',
        // bookTime: '2022-06-01 14:00',
        // startTime: 14,
        // endTime: 15,
        // checkinTime: '-',
        // status: 'booking',
      },
      is_booked: false,
      notifications: [],
      current_position: '',
    };
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
        this.booking = data;
      },
      (response) => {
        console.log(response)
        if (response.status == 404) {
          this.is_booked = false;
        }
        else {
          this.notifications.push({
            type: "danger",
            message: "查询当前预约情况失败 " + JSON.stringify(response.body.detail),
          });
        }
      }
    )
  },

  methods: {
    checkin () {
      this.$http.post(backend_link + "current_booking", {
        position: this.current_position
      }, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .then(
        (response) => {
          this.$router.push({ name: "history" });
        },
        (response) => {
          this.notifications.push({
            type: "danger",
            message: "签到失败 " + JSON.stringify(response),
          });
        }
      );
    },
    cancel () {
      this.$http
        .delete(backend_link + "current_booking", {
          headers: {
            "Content-Type": "application/json",
          },
        })
        .then(
          (response) => {
            this.$router.push({ name: "history" });
          },
          (response) => {
            this.notifications.push({
              type: "danger",
              message: "取消失败",
            });
          }
        );
    },
    to_time(i) {
      return (i < 10 ? '0' : '') + (i) + ':00';
    },
    to_date(i) {
      let date = new Date(i * 1000 * 86400)
      return date.getFullYear() + '.' + (date.getMonth() + 1) + '.' + date.getDate()
    },
  },

  components: {
    notification: Notification,
  },
};
</script>
