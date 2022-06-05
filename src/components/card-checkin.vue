<template>
  <div id="history">
    <h1>刷卡签到</h1>

    <notification v-bind:notifications="notifications"></notification>

    <div>

      <form v-on:submit.prevent="checkin">
        <div class="form-group">
          <label name="building_number">楼栋</label>
          <input
            type="text"
            class="form-control"
            v-model="buildingNumber"
            placeholder="手动填写，如：JB, GHX, Z"
            id="building_number"
            required
          />
        </div>
        <div class="form-group">
          <label name="classroom_number">教室</label>
          <input
            type="text"
            class="form-control"
            v-model="classRoomNumber"
            placeholder="手动填写，如：JB101, GHX502, Z2201"
            id="classroom_number"
            required
          />
        </div>
        <div class="form-group">
          <label name="card_id">卡号</label>
          <input
            type="text"
            class="form-control"
            v-model="cardId"
            placeholder="刷卡自动填写(未实现)"
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

let auth = store.state.auth;


export default {
  data() {
    return {
      buildingNumber: '',
      classRoomNumber: '',
      notifications: [],
      cardId: '',
    };
  },
  
  created: function () {},

  methods: {
    checkin () {
      this.$http.post(backend_link + "card_checkin", {
        buildingNumber: this.buildingNumber,
        classRoomNumber: this.classRoomNumber,
        cardId: this.cardId
      }, {
        headers: {
          "Content-Type": "application/json",
        },
      })
      .then(
        (response) => {
          let text = response.name + ' 座位号' + response.seatNumber + ' 时间' + response.startTime + '-' + response.endTime;
          this.notifications.push({
            type: "success",
            message: "签到成功\n" + text,
          });
        },
        (response) => {
          this.notifications.push({
            type: "danger",
            message: "签到失败 " + JSON.stringify(response),
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
