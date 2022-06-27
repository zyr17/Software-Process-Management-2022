<template>
  <div id="history">
    <h1>查看历史预定</h1>

    
    <table class="table table-hover">
      <thead>
        <tr>
          <td>教室</td>
          <!-- <td>座位号</td> -->
          <td>预定时间</td>
          <td>自习时间</td>
          <td>签到/取消时间</td>
          <td>状态</td>
          <td></td>
        </tr>
      </thead>

      <tbody>
        <tr v-for="history in histories">
          <td>{{ history.buildingNumber }} {{ history.classRoomNumber }}</td>
          <!-- <td>{{ history.seatNumber }}</td> -->
          <td>{{ new Date(history.bookTimeStamp) }}</td>
          <td>{{ to_date(history.date) }} {{ to_time(history.startTime) }}-{{ to_time(history.endTime + 1) }}</td>
          <td v-if="history.type == 'booked'"></td>
          <td v-if="history.type == 'checkin'">{{ Date(history.checkinTimeStamp) }}</td>
          <td v-if="history.type == 'cancel'">{{ Date(history.cancelTimeStamp) }}</td>
          <td>{{ statusName[history.type] }}</td>
          <td>
            <button
              v-if="history.type != 'booked'"
              @click="reBook(history)"
              class="btn btn-primary"
              disabled
              >快速重新预定</button>
            <button
              v-if="history.type == 'booked'"
              @click="detail"
              class="btn btn-primary"
              >详细</button>
            <button
              v-else
              @click="deleteHistory(history)"
              class="btn btn-danger"
              >删除记录</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Notification from "./notifications.vue";

import { backend_link } from "../const.vue";

import store from "../store";

let auth = store.state.auth;

export default {
  data() {
    return {
      statusName: {
        'booked': '预定中',
        'cancel': '已取消',
        'checkin': '已签到',
        'failed': '已爽约'
      },
      histories: [
          // {
          //   id: 1,
          //   buildingNumber: 'JB',
          //   classRoomNumber: '101',
          //   seatNumber: '25',
          //   bookTime: '2022-06-01 14:00',
          //   startTime: 14,
          //   endTime: 14,
          //   checkinTime: '-',
          //   status: 'booking',
          // },
          // {
          //   id: 2,
          //   buildingNumber: 'JB',
          //   classRoomNumber: '101',
          //   seatNumber: '25',
          //   bookTime: '2022-04-01 14:00',
          //   startTime: 14,
          //   endTime: 14,
          //   checkinTime: '2022-04-01 13:57',
          //   status: 'done',
          // },
          // {
          //   id: 3,
          //   buildingNumber: 'JA',
          //   classRoomNumber: '202',
          //   seatNumber: '5',
          //   bookTime: '2022-03-01 14:00',
          //   startTime: 14,
          //   endTime: 14,
          //   checkinTime: '-',
          //   status: 'cancelled',
          // },
          // {
          //   id: 4,
          //   buildingNumber: 'JA',
          //   classRoomNumber: '202',
          //   seatNumber: '5',
          //   bookTime: '2022-03-01 14:00',
          //   startTime: 14,
          //   endTime: 14,
          //   checkinTime: '-',
          //   status: 'failed',
          // }
      ],
      notifications: [],
    };
  },
  
  created: function () {
    this.getHistory()
  },

  methods: {
    getHistory() {
      this.$http.get(backend_link + 'history/' + store.state.id, {
        headers: {
          'Auth-Token': store.state.auth
        }
      }).then(
        (response) => {
          this.histories = response.data;
        },
        (response) => {
          store.commit('setNotification', {
            type: "danger",
            message: "历史记录获取失败 " + JSON.stringify(response.body.detail),
          });
        }
    )
    },
    reBook (history) {
      alert('未实现');
    },
    detail () {
      this.$router.push({ name: "checkin" });
    },
    deleteHistory (history) {
      this.$http
        .delete(backend_link + "history/" + store.state.id, 
        {
          body: history,
          headers: {
            'Auth-Token': store.state.auth
          },
        })
        .then(
          (response) => {
            store.commit('setNotification', {
              type: "success",
              message: "历史记录删除成功"
            });
            this.getHistory()
          },
          (response) => {
            store.commit('setNotification', {
              type: "danger",
              message: "历史记录删除失败 " + JSON.stringify(response.body.detail),
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
    }
  },

  components: {
    notification: Notification,
  },
};
</script>
