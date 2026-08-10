package com.z1.zoe.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.z1.zoe.R
import com.z1.zoe.model.SimpleEntry

class SimpleEntryAdapter(private val items: List<SimpleEntry>) : RecyclerView.Adapter<SimpleEntryAdapter.EntryViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EntryViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_simple_entry, parent, false)
        return EntryViewHolder(view)
    }

    override fun onBindViewHolder(holder: EntryViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    class EntryViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val title: TextView = itemView.findViewById(R.id.entryTitle)
        private val description: TextView = itemView.findViewById(R.id.entryDescription)

        fun bind(item: SimpleEntry) {
            title.text = item.title
            description.text = item.description
        }
    }
}
