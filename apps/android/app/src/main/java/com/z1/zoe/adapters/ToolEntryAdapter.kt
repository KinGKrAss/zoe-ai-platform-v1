package com.z1.zoe.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.z1.zoe.R
import com.z1.zoe.model.ToolEntry

class ToolEntryAdapter(private val items: List<ToolEntry>) : RecyclerView.Adapter<ToolEntryAdapter.ToolViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ToolViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_tool_entry, parent, false)
        return ToolViewHolder(view)
    }

    override fun onBindViewHolder(holder: ToolViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    class ToolViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val name: TextView = itemView.findViewById(R.id.toolName)
        private val permission: TextView = itemView.findViewById(R.id.toolPermission)
        private val description: TextView = itemView.findViewById(R.id.toolDescription)

        fun bind(item: ToolEntry) {
            name.text = item.name
            permission.text = item.permission
            description.text = item.description
        }
    }
}
