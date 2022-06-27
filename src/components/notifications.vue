<template>
    <div id="notifications">
        <div v-for="notification in notifications" :class="getNotificationClass(notification)">
            {{ notification.message }}
        </div>
    </div>
</template>

<script>

    import { notification_timeout } from '../const.vue'
    import store from '../store';

    export default{
        data(){
            return{
                fresh_key: false
            }
        },

        computed: {
            notifications () {
                this.fresh_key
                let res = [];
                for (let i of store.state.notifications) {
                    // console.log(i.notification_time.getTime(), notification_timeout, new Date().getTime())
                    if (i.notification_time.getTime() + notification_timeout > new Date().getTime())
                        res.push(i)
                }
                return res;
            }
        },

        created: function () {
            setInterval(function () {
                this.fresh_key = !this.fresh_key
            }.bind(this), 1000)
        },

        methods: {
            getNotificationClass: function(notification)
            {
                return 'alert alert-' + notification.type;
            }
        },

    }
</script>
