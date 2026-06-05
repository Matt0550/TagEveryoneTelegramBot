import { publicApiGetUserGroups } from '@/api/sdk.gen';
import type {
  PublicApiGetUserGroupsData,
  GroupsResponse,
} from '@/api/types.gen';
import { apiData } from '@/services/apiRuntime';
import { client } from '@/api/client.gen';

export interface GroupSettings {
  id: string;
  auto_add_new_members: boolean;
  auto_add_list_ids: string[];
}

export interface GroupSettingsUpdate {
  auto_add_new_members?: boolean;
  auto_add_list_ids?: string[];
}

export const groupService = {
  getUserGroups(query?: NonNullable<PublicApiGetUserGroupsData['query']>): Promise<GroupsResponse> {
    return apiData<GroupsResponse>(
      publicApiGetUserGroups({ query })
    );
  },

  checkIsAdmin(groupId: string): Promise<{ message: { is_admin: boolean }, success: boolean }> {
    return apiData<{ message: { is_admin: boolean }, success: boolean }>(
      client.get({ url: `/api/v1/public/groups/${groupId}/is-admin` } as any)
    );
  },

  getGroupSettings(groupId: string): Promise<GroupSettings> {
    return apiData<GroupSettings>(
      client.get({ url: `/api/v1/public/groups/${groupId}/settings` } as any)
    );
  },

  updateGroupSettings(groupId: string, data: GroupSettingsUpdate): Promise<GroupSettings> {
    return apiData<GroupSettings>(
      client.put({ url: `/api/v1/public/groups/${groupId}/settings`, body: data } as any)
    );
  }
};
