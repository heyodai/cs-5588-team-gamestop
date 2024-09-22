<template>
    <v-container>
        <v-row>
            <v-col cols="12">
                <v-card>
                    <v-list>
                        <v-list-item-group v-model="selectedItem">
                            <v-list-item v-for="message in messages" :key="message.id">
                                <v-list-item-content>
                                    <v-list-item-title>{{ message.text }}</v-list-item-title>
                                </v-list-item-content>
                            </v-list-item>
                        </v-list-item-group>
                    </v-list>
                </v-card>
                <v-text-field label="Type a message..." v-model="newMessage" :rules="[rules.required]"
                    append-icon="mdi-send" @click:append="sendMessage"></v-text-field>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import axios from 'axios';
export default {
    data: () => ({
        messages: [],
        newMessage: '',
        selectedItem: null,
        rules: {
            required: value => !!value || 'Required.',
        },
    }),
    methods: {
        fetchMessages() {
            // TODO: API call to fetch messages
            axios.get('http://localhost:8000/messages')
                .then(response => {
                    this.messages = response.data;
                })
                .catch(error => console.error('Error fetching messages:', error));
        },
        sendMessage() {
            if (this.newMessage) {
                // TODO: API call to send this.newMessage
                axios.post('http://127.0.0.1:8000/send', { text: this.newMessage })
                    .then(response => {
                        this.messages.push(response.data);  // Assuming the API returns the sent message
                    })
                    .catch(error => console.error('Error sending message:', error));
                this.newMessage = ''; // clear message input after sending
            }
        }
    },
    mounted() {
        this.fetchMessages();
    }
}
</script>

<style scoped></style>