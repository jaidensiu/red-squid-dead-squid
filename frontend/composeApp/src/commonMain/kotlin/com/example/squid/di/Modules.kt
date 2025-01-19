package com.example.squid.di

import com.example.squid.ui.players.PlayersViewModel
import org.koin.core.module.dsl.viewModelOf
import org.koin.dsl.module

val sharedModule = module {
    viewModelOf(::PlayersViewModel)
}
