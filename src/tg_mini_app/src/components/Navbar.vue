<script setup lang="ts">
import { useUser } from '@/composables/useUser'
import { useAuth } from '@/composables/useAuth'
import { useMiniApp } from 'vue-tg'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuPortal, DropdownMenuSubContent, DropdownMenuRadioGroup, DropdownMenuRadioItem } from '@/components/ui/dropdown-menu'
import { Globe } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { setAppLocale } from '@/i18n'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle
} from '@/components/ui/navigation-menu'

const { user } = useUser()
const { logout } = useAuth()
const miniApp = useMiniApp()
const isInsideTelegram = !!miniApp.initData

const getInitials = (firstName?: string, lastName?: string) => {
  if (!firstName) return 'U'
  return `${firstName.charAt(0)}${lastName ? lastName.charAt(0) : ''}`.toUpperCase()
}

const { t, locale } = useI18n()
</script>

<template>

  <header
    class="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="container flex h-14 max-w-screen-2xl items-center justify-between px-4 w-full">
      <NavigationMenu>
        <NavigationMenuList>
          <NavigationMenuItem v-if="!isInsideTelegram">
            <NavigationMenuLink as-child :class="navigationMenuTriggerStyle()">
              <router-link to="/">{{ t('nav.brand') }}</router-link>
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink as-child :class="navigationMenuTriggerStyle()">
              <router-link to="/">{{ t('nav.groups') }}</router-link>
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink as-child :class="navigationMenuTriggerStyle()">
              <router-link to="/admin">{{ t('nav.admin') }}</router-link>
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      <div class="flex items-center" v-if="user">
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" class="relative h-8 w-8 rounded-full">
              <Avatar class="h-8 w-8">
                <AvatarFallback>{{ getInitials(user.first_name, user.last_name) }}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent class="w-56" align="end">
            <DropdownMenuLabel class="font-normal flex">
              <div class="flex flex-col space-y-1">
                <p class="text-sm font-medium leading-none">{{ user.first_name }} {{ user.last_name || '' }}</p>
                <p class="text-xs leading-none text-muted-foreground">
                  @{{ user.username || 'user' }}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <Globe class="mr-2 h-4 w-4" />
                <span>{{ t('actions.language') }}</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent>
                  <DropdownMenuRadioGroup :model-value="locale" @update:model-value="setAppLocale">
                    <DropdownMenuRadioItem value="en">
                      {{ t('actions.english') }}
                    </DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="it">
                      {{ t('actions.italian') }}
                    </DropdownMenuRadioItem>
                  </DropdownMenuRadioGroup>
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
            
            <template v-if="!isInsideTelegram">
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="logout">
                {{ t('actions.logOut') }}
              </DropdownMenuItem>
            </template>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

    </div>
  </header>
</template>
