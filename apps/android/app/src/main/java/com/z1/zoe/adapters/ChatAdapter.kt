package com.z1.zoe.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.z1.zoe.R
import com.z1.zoe.model.ChatMessage

class ChatAdapter(messages: List<ChatMessage>) : RecyclerView.Adapter<ChatAdapter.ChatViewHolder>() {

    private val items = messages.toMutableList()

    fun addMessage(message: ChatMessage) {
        items.add(message)
        notifyItemInserted(items.lastIndex)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_chat_message, parent, false)
        return ChatViewHolder(view)
    }

    override fun onBindViewHolder(holder: ChatViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    class ChatViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val sender: TextView = itemView.findViewById(R.id.chatSender)
        private val content: TextView = itemView.findViewById(R.id.chatContent)

        fun bind(message: ChatMessage) {
            sender.text = message.sender
            content.text = message.content
        }
    }
}
