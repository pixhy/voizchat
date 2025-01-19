<script setup lang="ts">

</script>
<template>
    <RouterLink exactActiveClass="active" to="/friends">All</RouterLink>
    <RouterLink exactActiveClass="active" to="/friends/incoming">Incoming</RouterLink>
    <RouterLink exactActiveClass="active" to="/friends/outgoing">Outgoing</RouterLink>
</template>

<style>
.active {
    color: deeppink;
}
</style>