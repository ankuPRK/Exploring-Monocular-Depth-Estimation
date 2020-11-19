import sys
sys.path.append('./../')
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.init import xavier_uniform_, zeros_
import models
from utils import save_checkpoint, log_output_tensorboard
import utils
import pdb
import numpy as np
import pdb
st = pdb.set_trace
import matplotlib.pyplot as plt
torch.manual_seed(125)
torch.cuda.manual_seed_all(125) 
torch.backends.cudnn.deterministic = True
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# import numpy as np
class Runner(nn.Module):
    def __init__(self, args):
        super(Runner, self).__init__()
        self.hidden_dim = 128
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.disp_net = models.DispNet().to(self.device)
        self.pose_net = models.PoseNet(nb_ref_imgs=args.sequence_length-1,output_exp=True).to(self.device)

        if args.pretrained_exp_pose:
            print("=> using pre-trained weights for explainabilty and pose net")
            weights = torch.load(args.pretrained_exp_pose)
            self.pose_net.load_state_dict(weights['state_dict'], strict=False)
        else:
            self.pose_net.init_weights()

        if args.pretrained_disp:
            print("=> using pre-trained weights for Dispnet")
            weights = torch.load(args.pretrained_disp)
            self.disp_net.load_state_dict(weights['state_dict'])
        else:
            self.disp_net.init_weights()
        self.args = args
        self.l1_loss = nn.L1Loss()

    
    def forward(self, tgt_img, log_losses, log_output, tb_writer, n_iter, ret_depth, mode = 'train'):

        # compute output
        w1, w2, w3 ,w4 = 1,1,1,1 #TODO set weights for various losses here
        # st()
        # disparities = self.disp_net(self.__p(rgbs_from_first), self.__p(optical_codes), self.__u)
        disparities =[1,1]
        if type(disparities) not in [tuple, list]:
            disparities = [disparities]
        depth = [1/disp for disp in disparities]
        depth = torch.ones(tgt_img.shape).to(device)
        if ret_depth: #inference call
            return depth

        # _, pose = self.pose_exp_net(depth[0], rgbs_from_first, self.__p, self.__u)	# pose = [seq_len-2, batch , 6]


        ###############################################
        # Calculating losses
        ###############################################

        #### code for loss calculation
        loss = self.l1_loss(depth, tgt_img)
        # loss['a'] = 0
        # loss['b'] = 0#SECONDARY LOSS
        ###############################################
        # Logging
        ###############################################
        # if log_losses:
        #     # print("Logging Scalars")
        #     tb_writer.add_scalar(mode+'/photometric_loss', loss_1.item(), n_iter)
        #     if w1 > 0:
        #         tb_writer.add_scalar(mode+'/explanability_loss', loss_2.item(), n_iter)
        #         tb_writer.add_scalar(mode+'/appearance_loss', ap_loss.item(), n_iter)
        #         tb_writer.add_scalar(mode+'/SSIM_loss', loss_4.item(), n_iter)
        #     if w2 > 0:
        #         tb_writer.add_scalar(mode+'/disparity_smoothness_loss', depth_reg_loss.item(), n_iter)
        #     if w4 > 0:
        #         tb_writer.add_scalar(mode+'/GAN_loss', gan_loss.item(), n_iter)
        #     if w3 > 0:
        #         tb_writer.add_scalar(mode+'/traj_loss', traj_loss.item(), n_iter)
        #     tb_writer.add_scalar(mode+'/total_loss', loss.item(), n_iter)

        # if log_output: 
        #     # print("Logging Images")
        #     tb_writer.add_image(mode+'/train_input', tensor2array(tgt_img[0]), n_iter)
        #     flow_to_show=vis_optflow(optical_flow_imgs[0][0].permute(1,2,0).cpu().numpy())
        #     tb_writer.add_image(mode+'/train_optical_flow', flow_to_show, n_iter)
        #     # st()
        #     output_depth = depth[0][-1,0,:,:,:]
        #     tb_writer.add_image(mode+'/train_depth', tensor2array(output_depth[0], max_value=None), n_iter)
        #     output_disp = 1.0/output_depth
        #     tb_writer.add_image(mode+'/train_disp', tensor2array(output_disp[0], max_value=None, colormap='magma'), n_iter)
        #     tb_writer.add_image(mode+'/train_warped', tensor2array(warped[0][-1][0,:,:,:]), n_iter)
        #     tb_writer.add_image(mode+'/train_diff', tensor2array(diff[0][-1][0,:,:,:]*0.5), n_iter)
        #     mask_to_show = tensor2array(explainability_mask[0][0][0], max_value=1, colormap='bone')
        #     tb_writer.add_image(mode+'/train_exp_mask', mask_to_show, n_iter)

        return loss